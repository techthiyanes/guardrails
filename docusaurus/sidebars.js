/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// populate examples from examples folder. Only include .mdx and .md files
const fs = require("fs");

// @ts-check
/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */

// get examples from the file called examples-toc.json

const examples = JSON.parse(fs.readFileSync("./docusaurus/examples-toc.json", "utf8")).find(x => x.label === "Examples");

const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  // tutorialSidebar: [{ type: "autogenerated", dirName: "." }],
  docsSidebar: [
        {
          type: "doc",
          label: "Introduction",
          id: "index"
        },
        {
          type: "doc",
          label: "Installation",
          id: "guardrails_ai/installation"
        },
        {
          type: "doc",
          label: "Getting Started",
          id: "guardrails_ai/getting_started"
        },
        {
          type: "category",
          label: "Defining Guardrails",
          collapsed: true,
          items: [
            "defining_guards/pydantic",
            "defining_guards/strings",
            "defining_guards/rail",
          ]
        },
        {
          type: "category",
          label: "Concepts",
          collapsed: true,
          items: [
            "concepts/guard",
            "concepts/validators",
            "concepts/output",
            "concepts/prompt",
            "concepts/instructions",
            "concepts/logs",
            "concepts/envars",
          ]
        },
        {
          type: "doc",
          id: "faq",
          label: "Validator Library"
        },
        {
          type: "category",
          label: "API Reference",
          collapsed: true,
          items: [
            {
              type: "autogenerated",
              dirName: "api_reference_markdown/markdown"
            }
          ]
        },
        {
          type: "category",
          label: "Migration Guides",
          collapsed: true,
          items: [
            "migration_guides/0-2-migration"
          ],
        },
        {
          type: "doc",
          id: "faq",
          label: "FAQ"
        },
        examples,
        {
          type: "category",
          label: "Integrations",
          collapsed: true,
          items: [
            {
              type: "autogenerated",
              dirName: "integrations"
            }
          ]
        }
  ]
};

module.exports = sidebars;
