// Source: TypeScript Benign Sample
// Generated: 2026-04-02 11:48:04.520005

#!/usr/bin/env ts-node
/**
 * LangChain.js Agent 示例 - 良性
 */
import { ChatOpenAI } from "@langchain/openai";
import { AgentExecutor, createOpenAIFunctionsAgent } from "langchain/agents";

const model = new ChatOpenAI({ temperature: 0 });
const tools = [];

const agent = createOpenAIFunctionsAgent({
  llm: model,
  tools,
  prompt: null,
});

const executor = new AgentExecutor({
  agent,
  tools,
});

console.log("Agent initialized");
