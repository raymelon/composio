import { Composio, LangchainToolSet } from "composio-core";
import { z } from "zod";

const toolset = new LangchainToolSet({
    apiKey: "4q7w9q6evy2fiisjgwoc8i"
});

(async() => {

    const result = await toolset.client.actions.findActionEnumsByUseCase({
        apps: ["gmail", "googledrive"],
        useCase: "get repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo informationget repo information",
        limit: 5
    });

    console.log("Action result:", result);
})();