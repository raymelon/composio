import { generateText, streamText } from "ai";
import { openai } from "@ai-sdk/openai";
import { VercelAIToolSet } from 'composio-core';
import { z } from 'zod';
import postgres from 'postgres';
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const { messages } = await req.json();
    let finalResult;
    const sys = `
    You are a JIRA agent. You help the user execute JIRA actions.
When editing the issue, you need to pass the update parameter in the Edit Issue action.
Here's a sample request body for the Edit Issue action:
{"issueIdOrKey":"10039","notifyUsers":true,"overrideScreenSecurity":false,"overrideEditableFlag":false,"returnIssue":false,"update":{"description":[{"set":{"type":"doc","version":1,"content":[{"type":"paragraph","content":[{"type":"text","text":"This is the updated description for the Jira issue."}]}]}}]}}
`
    // Setup toolset
    const toolset = new VercelAIToolSet({
      apiKey: process.env.COMPOSIO_API_KEY,
    });



    async function executeAgent(entityName: string | undefined) {
      // setup entity
      const entity = await toolset.client.getEntity(entityName);
      const messageHistory = [];

      const tools = await toolset.getTools({
        actions: [ 
          "JIRA_CREATE_ISSUE",
          "JIRA_GET_ISSUE_TYPES_FOR_PROJECT",
          "JIRA_GET_ALL_PROJECTS",
          "JIRA_UPDATE_ISSUE_FIELD_OPTION",
          "JIRA_UPDATE_ISSUE_TYPE",
          "JIRA_UPDATE_ISSUE_LINK_TYPE",
          "JIRA_GET_PROJECT",
          "JIRA_UPDATE_ISSUE_TYPE_SCHEME",
          "JIRA_UPDATE_ISSUE_LINK_TYPE",
          "JIRA_EDIT_ISSUE"  
        ],
      });
      messageHistory.push({ role: "user", content: messages[messages.length - 1].content });

      // Store both the AI response and tool execution result
      const aiResponse = await generateText({
        model: openai("gpt-4o"),
        tools,
        toolChoice: "auto",
        system:sys,
        messages: messages,
      });

      let finalResult = null;
      if (aiResponse.toolCalls && aiResponse.toolCalls.length > 0) {
        finalResult = await toolset.executeToolCall(
          {
            name: aiResponse.toolCalls[0].toolName, 
            arguments: aiResponse.toolCalls[0].args
          },
          entity.id
        );
        console.log(finalResult);
      }
      console.log(aiResponse);

      const res = await streamText({
        model: openai('gpt-4o'),
        prompt: finalResult 
            ? `Given the following user request: "${messages[messages.length - 1].content}", here's what happened: ${aiResponse.text} and the result was: ${finalResult}. Reveal the result of the tool call without markdown. This is the database that you need to use the actions on. Do not summarize the result, just show the output of the tool call in a readable and summarized manner, not in the same json format.`
            : `Print this same text, without adding any other text or sentences before or after: ${aiResponse.text}`,
      });
      messageHistory.push({ role: "assistant", content: res.text });
      
      return res.toDataStreamResponse();
    }

    const result = await executeAgent("default");
    
    return result;

  } catch (error) {
    console.error('Error:', error);
    return NextResponse.json({
      role: 'assistant',
      content: 'Sorry, there was an error processing your request.'
    }, { status: 500 });
  }
}
