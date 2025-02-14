# extract_classify.txt
- **Purpose:** To extract relevant information and classify it accurately.
- **Content:** Include detailed instruction sets that guide the process of:
    - Identifying key elements in input data.
    - Categorizing information based on predefined criteria.
- **Usage:** This file is referenced when data needs to be parsed for structuring and classification tasks. A `{labels}` tag must be provided in the file where the current list of labels will be injected. The AI will have a tool `label_text` provided where it will attempt to categorize information found in the document. The labels tag allows subsequent chats to reuse labels.

# summarize_category.txt
- **Purpose:** To summarize and condense data from categorized input.
- **Content:** Include clear instructions to produce summaries that:
    - Capture the essence of the input text.
    - Provide brief overviews suitable for quick review.
- **Usage:** This file is used to generate high-level overviews after classification is performed using the prompts from *extract_classify.txt*.