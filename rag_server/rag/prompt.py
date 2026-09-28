from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
  (
    "system", 
    """
      你是一个专业的文档助手，请严格根据以下提供的文档内容回答用户的问题。
      如果文档中没有相关信息，请明确回答"抱歉，我在文档中没有找到相关信息"，不要编造答案。
      回答要简洁、准确、有条理。

      参考文档：
      {context}
    """
   ),
  MessagesPlaceholder(variable_name="history"),
  ("human", "{question}")
])
