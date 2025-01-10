import { beforeAll, describe, expect, it } from "@jest/globals";
import { z } from "zod";
import { getTestConfig } from "../../config/getTestConfig";
import { ActionExecuteResponse } from "../sdk/models/actions";
import { LlamaIndexToolSet } from "./llamaindex";

describe("Apps class tests", () => {
  let llamaindexToolSet: LlamaIndexToolSet;
  beforeAll(() => {
    llamaindexToolSet = new LlamaIndexToolSet({
      apiKey: getTestConfig().COMPOSIO_API_KEY,
      baseUrl: getTestConfig().BACKEND_HERMES_URL,
    });
  });

  it("getools", async () => {
    const tools = await llamaindexToolSet.getTools({
      apps: ["github"],
    });
    expect(tools).toBeInstanceOf(Array);
  });
  it("check if tools are coming", async () => {
    const tools = await llamaindexToolSet.getTools({
      actions: ["GITHUB_GITHUB_API_ROOT"],
    });
    expect(tools.length).toBe(1);
  });
  it("check if getTools, actions are coming", async () => {
    const tools = await llamaindexToolSet.getTools({
      actions: ["GITHUB_GITHUB_API_ROOT"],
    });

    expect(tools.length).toBe(1);
  });
  it("Should create custom action to star a repository", async () => {
    await llamaindexToolSet.createAction({
      actionName: "starRepositoryCustomAction",
      toolName: "github",
      description: "This action stars a repository",
      inputParams: z.object({
        owner: z.string(),
        repo: z.string(),
      }),
      callback: async (
        inputParams,
        _authCredentials,
        executeRequest
      ): Promise<ActionExecuteResponse> => {
        const res = await executeRequest({
          endpoint: `/user/starred/${inputParams.owner}/${inputParams.repo}`,
          method: "PUT",
          parameters: [],
        });
        return res;
      },
    });

    const tools = await llamaindexToolSet.getTools({
      actions: ["starRepositoryCustomAction"],
    });

    await expect(tools.length).toBe(1);
    const actionOuput = await llamaindexToolSet.executeAction({
      action: "starRepositoryCustomAction",
      params: {
        owner: "composioHQ",
        repo: "composio",
      },
      entityId: "default",
      connectedAccountId: "9442cab3-d54f-4903-976c-ee67ef506c9b",
    });

    expect(actionOuput).toHaveProperty("successful", true);
  });
});
