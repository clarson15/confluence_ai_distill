# agentic_rag.txt

This prompt outlines a retrieval-augmented generation approach for building a specialized AI agent. Your prompt should include:

* Use the custom function get_document(page_id) to fetch relevant information.
* Navigate a hierarchical source structure efficiently, enabling deeper exploration.
* Consolidate findings into a complete final answer.
* Stay strictly factual avoiding opinions, commentary, and assumptions.
* Initial page ids (space homepages) as entrypoints to begin searching

# agentic_host.txt

This prompt defines the conversational host interface for the AI system. Your prompt should include:

* Instructions for maintaining a helpful, friendly tone while guiding users
* Use the custom function lookup_info(prompt) to ask the RAG agent a question
* Clear definition of user interaction patterns and conversation flow
* Guidelines for presenting information retrieved by the RAG component
* Rules for maintaining context across multi-turn conversations
* Methods for clarifying user requests when needed
* Parameters for generating concise, relevant responses
* Approach for handling questions outside the knowledge domain
* Format specifications for structuring complex information