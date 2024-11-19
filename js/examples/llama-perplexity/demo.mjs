import { Hono } from 'hono';
import { OpenAIToolSet } from "composio-core";
import OpenAI from "openai";
import Groq from 'groq-sdk';

const app = new Hono();

const setupUserConnection = async (toolset, entityId) => {
  const entity = await toolset.client.getEntity(entityId);
  const connection = await entity.getConnection('github');
  if (!connection) {
    const newConnection = await entity.initiateConnection('github');
    console.log('Log in via: ', newConnection.redirectUrl);
    return { redirectUrl: newConnection.redirectUrl, message: 'Please log in to continue and then call this API again' };
  }
  return connection;
};

app.post('/', async (c) => {
  try {
    const groqClient = new Groq({ apiKey: c.env.GROQ_API_KEY });
    const toolset = new OpenAIToolSet({ apiKey: c.env.COMPOSIO_API_KEY });

    const entity = await toolset.client.getEntity('default2');
    const connection = await setupUserConnection(toolset, entity.id);
    if (connection.redirectUrl) return c.json(connection);

    const tools = await toolset.getTools({ actions: ['github_issues_create'] }, entity.id);
    const response = await groqClient.chat.completions.create({
      model: "llama3-8b-8192",
      messages: [
        { role: "system", content: "You are an AI Search Engine. You are given a query and you need to search the web for the best answer to the query. You can use the tools provided to you to search the web." },
        { role: "user", content: "What is the weather in Tokyo?" }
      ],
      tools,
      tool_choice: "auto",
    });

    const result = await toolset.handleToolCall(response, entity.id);
    return c.json({ message: "Issue has been created successfully", result });
  } catch (err) {
    console.error('Error:', err);
    return c.json({ error: 'An unexpected error occurred' }, 500);
  }
});

export default app;
