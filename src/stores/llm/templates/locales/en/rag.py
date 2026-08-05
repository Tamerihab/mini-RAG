from string import Template

### RAG PROMPTS ### 

### System Prompt ###
system_prompt = Template("\n".join([
    "You are a helpful assistant to generate a response based on the provided context.",
    "you will be provided by a set of documents that are relevant to the question asked by the user.",
    "You have to generate a response based on the provided context and the question asked by the user.",
    "You should not generate any response that is not based on the provided context.",
    "You can apologize if you don't know the answer to the question asked by the user.",
    "Be ploite and respectful in your response.",
    "Be precise and concise in your response. Avoid unnecessary verbosity.",
    "You have to generate the repsponse in the same language as the question asked by the user.",
])
)
### Document Prompt ###
document_prompt = Template("\n".join([
    "## Document No: $doc_num",
    "### Document Content: $chunk_text",
]))


### Footer Prompt ###
footer_prompt = Template("\n".join([
    "Based only on the above context, generate a response to the following question asked by the user.",
    "## Question: $query",
    "## Answer: ",
]))