import { describe, it, expect, beforeAll } from "@jest/globals";
import { getBackendClient } from "../testUtils/getBackendClient";

import { Triggers } from "./triggers";
import { ConnectedAccounts } from "./connectedAccounts";
import { Entity } from "./Entity";
import { Actions } from "./actions";
import { SDK_ERROR_CODES } from "../utils/errors/src/constants";

describe("Apps class tests", () => {
  let backendClient;
  let triggers: Triggers;
  let connectedAccounts: ConnectedAccounts;
  let entity: Entity;

  let triggerId: string;
  let actions: Actions;

  beforeAll(() => {
    backendClient = getBackendClient();
    triggers = new Triggers(backendClient);
    connectedAccounts = new ConnectedAccounts(backendClient);
    entity = new Entity(backendClient, "default");
    connectedAccounts = new ConnectedAccounts(backendClient);
    actions = new Actions(backendClient);
  });

  it("should create an Apps instance and retrieve apps list", async () => {
    const triggerList = await triggers.list();
    expect(triggerList.length).toBeGreaterThan(0);
  });

  it("should retrieve a list of triggers for a specific app", async () => {
    const appName = "github";
    const triggerList = await triggers.list({
      appNames: [appName],
    });
    // this is breaking for now
    expect(triggerList.length).toBeGreaterThan(0);
    expect(triggerList[0].appName).toBe(appName);
  });
});

describe("Apps class tests subscribe", () => {
  let backendClient;
  let triggers: Triggers;
  let connectedAccounts: ConnectedAccounts;
  let actions: Actions;
  let entity: Entity;

  let triggerId: string;

  beforeAll(() => {
    backendClient = getBackendClient();
    triggers = new Triggers(backendClient);
    connectedAccounts = new ConnectedAccounts(backendClient);
    entity = new Entity(backendClient, "default");
    actions = new Actions(backendClient);
  });

  it("should create a new trigger for gmail", async () => {
    const connectedAccount = await connectedAccounts.list({
      user_uuid: "default",
    });

    const connectedAccountId = connectedAccount.items.find(
      (item) => item.appName === "gmail"
    )?.id;
    if (!connectedAccountId) {
      throw new Error("No connected account found");
    }
    const trigger = await triggers.setup({
      connectedAccountId,
      triggerName: "gmail_new_gmail_message",
      config: {
        userId: connectedAccount.items[0].id,
        interval: 60,
        labelIds: "INBOX",
      },
    });

    expect(trigger.status).toBe("success");
    expect(trigger.triggerId).toBeTruthy();

    triggerId = trigger.triggerId;
  });

  it("should disable, enable, and then disable the created trigger", async () => {
    let trigger = await triggers.disable({ triggerId });
    expect(trigger.status).toBe("success");

    trigger = await triggers.enable({ triggerId });
    expect(trigger.status).toBe("success");

    trigger = await triggers.disable({ triggerId });
    expect(trigger.status).toBe("success");
  });

  it("should retrieve a list of triggers for a specific triggerId", async () => {
    const triggerList = await triggers.list({
      triggerIds: ["GMAIL_NEW_GMAIL_MESSAGE"],
    });
    expect(triggerList.length).toBeGreaterThan(0);
    expect(triggerList[0].name).toBe("GMAIL_NEW_GMAIL_MESSAGE");
  });

  it("try to subscribe to a trigger that doesn't exist", async () => {
    await expect(
      triggers.subscribe(async () => {}, {
        triggerId: "GMAIL_NEW_GMAIL_MESSAGE_2",
      })
    ).rejects.toThrow("No triggers found for the given filters");
  });

  // it("should subscribe to a trigger and receive a trigger", async () => {
  //     function waitForTriggerReceived() {
  //         return new Promise((resolve) => {
  //             triggers.subscribe((data) => {
  //                 resolve(data);
  //             }, {
  //                 appName: "github",
  //                 triggerName: "GITHUB_ISSUE_ADDED_EVENT"
  //             });

  //             setTimeout(async () => {
  //                 const actionName = "github_create_an_issue";
  //                 // Not urgent
  //                 const connectedAccountsResult = await connectedAccounts.list({ integrationId: 'ca85b86b-1198-4e1a-8d84-b14640564c77' });
  //                 const connectionId = connectedAccountsResult.items[0].id;

  //                 await actions.execute({
  //                     actionName,
  //                     requestBody: {
  //                         connectedAccountId: connectionId,
  //                         input: {
  //                             title: "test",
  //                             owner: "ComposioHQ",
  //                             repo: "test_repo",
  //                         },
  //                         appName: 'github'
  //                     }
  //                 });
  //             }, 4000);
  //         });
  //     }

  //     const data = await waitForTriggerReceived();

  //     //@ts-ignore
  //     expect(data.payload.triggerName).toBe("GITHUB_ISSUE_ADDED_EVENT");

  //     triggers.unsubscribe();
  // });
});
