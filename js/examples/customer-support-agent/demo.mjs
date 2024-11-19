import express from 'express';
import { ChatOpenAI } from "@langchain/openai";
import { createOpenAIFunctionsAgent, AgentExecutor } from "langchain/agents";
import { pull } from "langchain/hub";
import dotenv from 'dotenv';
import { LangchainToolSet } from "composio-core";

dotenv.config()
const app = express();
const PORT = process.env.PORT || 2001;

app.use(express.json());

(async () => {
    try {
        const llm = new ChatOpenAI({
            model: "gpt-4o",
        });

        const toolset = new LangchainToolSet({
            apiKey: process.env.COMPOSIO_API_KEY,
        });

        const tools = await toolset.get_actions({
            actions: ["EXA_SEARCH", "GOOGLESHEETS_BATCH_UPDATE","WEBTOOL_SCRAPE_WEBSITE_CONTENT","RAGTOOL_ADD_CONTENT_TO_RAG_TOOL","LINEAR_LIST_LINEAR_PROJECTS","LINEAR_CREATE_LINEAR_ISSUE"]
        });

        const prompt = await pull("hwchase17/openai-functions-agent");

        // Debugging logs
        //console.log("LLM:", llm);
        console.log("Tools:", tools);
        //console.log("Prompt:", prompt);

        const additional = `
        EXECUTE ALL TOOL CALLS, You answer queries based on internet searches. First search each link then scrape the content and add it in RAG
        You query the RAG Vector Store first if the answer is satisfactory
        you create tickets in google spreadsheet, in the format of columns [queries] [solutions] and [resolved?] 
        Also create a linear issue if it is not resolved
        Return the final answer to the question
            `;

        // Check combined_prompt

        const agent = await createOpenAIFunctionsAgent({
            llm,
            tools,
            prompt,
        });

        const agentExecutor = new AgentExecutor({
            agent,
            tools,
            verbose: true,
        });
        const spreadsheet_id="1yTa_5uaX7_fRKiejpw6FitLTV04uGJHUUMV5v18Quoo"
        const sheet_name="Sheet1"
        const input_query = "What are best practices while using threejs?"
        const result = await agentExecutor.invoke({
            input: `
                EXECUTE ALL TOOL CALLS, You answer queries based on internet searches. First search each link then scrape the content and add it in RAG
                You query the RAG Vector Store first if the answer is satisfactory
                you create tickets in google spreadsheet, in the format of columns [queries] [solutions] and [resolved?] 
                Also create a linear issue if it is not resolved
                Return the final answer to the question
                The query is: ${input_query}
                The spreadsheet id is: ${spreadsheet_id}
                The sheet name is: ${sheet_name}
                `
        });

    } catch (error) {
        console.error(error);
    }
})();
