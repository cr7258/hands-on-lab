## 部署 embedding 模型

Elasticsearch 默认提供了以下 3 种模型，`.elser_model_2` 使用稀疏向量进行索引，对英文比较友好。如果是搜索非英文，建议使用 `.multilingual-e5-small` 模型。如果要导入第三方模型，可以参考该[文档](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-text-emb-vector-search-example.html)。

![CleanShot 2025-03-02 at 22 43 01@2x](https://github.com/user-attachments/assets/f1cecb48-c78a-4d5d-b2bc-a64d0e1e51f1)

## 创建索引

创建索引，重点设置两个字段：
- content：存储实际的文本，用户写入只需要写 content 字段，copy_to 参数确保内容被复制到 semantic_text 字段并由 embedding 模型进行向量化。
- semantic_text：存储 embedding 后的向量。semantic_text 类型的字段默认使用 `.elser-2-elasticsearch` 作为 embedding 模型，如果要使用其他模型，需要设置 [inference_id](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html)。

```yaml
PUT employee_handbook
{
  "mappings": {
    "properties": {
      "semantic_text": { 
        "type": "semantic_text"
      },
      "content": { 
        "type": "text",
        "copy_to": "semantic_text" 
      }
    }
  }
}
```

## 写入数据

```bash
POST _bulk
{"index": {"_index": "employee_handbook"}}
{"title": "Company Overview", "content": "Our company was founded in 2005 and is headquartered in Beijing. With a workforce of over 1,000 employees, we specialize in artificial intelligence and software development. Our vision is to enhance customer value through technological innovation and provide high-quality solutions to global clients.", "category": "Company Overview", "link": "https://workplace.org/rules/1854"}
{"index": {"_index": "employee_handbook"}}
{"title": "Employee Code of Conduct", "content": "Employees must adhere to professional ethics, maintain integrity, respect colleagues, and avoid conflicts of interest. Disclosing company confidential information, including customer data and internal research materials, is strictly prohibited. Violators may face fines of up to 100,000 CNY or legal consequences.", "category": "Code of Conduct", "link": "https://workplace.org/info/9931"}
{"index": {"_index": "employee_handbook"}}
{"title": "Attendance Policy", "content": "Employees must report to work on time. Working hours are from 9:00 AM to 6:00 PM, with a lunch break from 12:30 PM to 1:30 PM. Being late or leaving early more than 3 times will result in a warning, more than 5 times requires a written explanation, and more than 10 times may lead to salary deductions.", "category": "Attendance Management", "link": "https://guidelines.ai/handbook/4334"}
{"index": {"_index": "employee_handbook"}}
{"title": "Salary and Benefits", "content": "The company offers competitive salaries, with annual performance-based adjustments averaging an 8% increase. Bonuses include performance incentives (up to 20% of monthly salary) and year-end bonuses (1 to 3 months' salary). Benefits include social insurance, paid annual leave (12 days per year), and holiday allowances.", "category": "Salary & Benefits", "link": "https://workplace.org/policy/7457"}
{"index": {"_index": "employee_handbook"}}
{"title": "Performance Evaluation", "content": "Performance evaluations are conducted quarterly and annually, assessing goal completion (50%), teamwork (30%), and personal growth (20%). Employees scoring below 60 for a quarter must attend additional training. A consecutive low score may result in salary reduction or reassignment.", "category": "Performance Management", "link": "https://guidelines.ai/info/9582"}
{"index": {"_index": "employee_handbook"}}
{"title": "Career Development", "content": "The company provides internal training, external training subsidies (up to 3,000 CNY per year), and promotion opportunities. Every employee has at least two career development meetings per year and can apply for cross-department learning or participate in innovation projects to enhance their skills.", "category": "Career Development", "link": "https://docs.net/info/8827"}
{"index": {"_index": "employee_handbook"}}
{"title": "Security and Confidentiality", "content": "Employees must follow data security and confidentiality policies. All company devices must have official antivirus software installed. Accessing sensitive data requires two-factor authentication. Violations may result in suspension or termination. The company conducts security audits quarterly.", "category": "Information Security", "link": "https://workplace.org/rules/9086"}
{"index": {"_index": "employee_handbook"}}
{"title": "Leave and Vacation Policy", "content": "Employees are entitled to 10 days of sick leave, 12 days of annual leave (after one year of service), 3 to 10 days of marriage leave, and 98 days of maternity leave (15 days for paternity leave). All leave requests must be approved in advance. Unauthorized absences will be considered absenteeism.", "category": "Leave Policy", "link": "https://guidelines.ai/policy/3310"}
{"index": {"_index": "employee_handbook"}}
{"title": "Travel Policy", "content": "Business travel requests must be submitted at least 5 working days in advance and approved by direct supervisors and finance. The company reimburses reasonable expenses, including transportation, accommodation, and meals. Domestic accommodation is capped at 600 CNY per night, while international stays are capped at $150 per night.", "category": "Travel Regulations", "link": "https://guidelines.ai/rules/5144"}
{"index": {"_index": "employee_handbook"}}
{"title": "Employee Reward and Punishment System", "content": "The company rewards outstanding employees with quarterly bonuses (ranging from 2,000 to 10,000 CNY) and an annual outstanding employee award (up to 50,000 CNY). Violations of company policies will result in written warnings, and severe offenses may lead to salary reductions or termination.", "category": "Rewards & Punishments", "link": "https://guidelines.ai/handbook/9306"}
```

## 配置 ai-search 插件

另外还需要配置 ai-proxy 插件，这里省略。

```bash
needReference: true
searchFrom:
- contentField: "content"
  count: 1
  index: "employee_handbook"
  linkField: "link"
  password: "test123"
  semanticTextField: "semantic_text"
  serviceName: "elasticsearch.static"
  servicePort: 80
  timeoutMillisecond: 50000
  titleField: "title"
  type: "elasticsearch"
  username: "elastic"
# 可选参数
# searchRewrite:
#   llmApiKey: "<api-key>"
#   llmModelName: "qwen-long"
#   llmServiceName: "llm-aliyun.internal.dns"
#   llmServicePort: 443
#   llmUrl: "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
#   timeoutMillisecond: 15000
```

#### 验证

```bash
curl 'http://localhost:8080/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -d '{
    "model": "qwen-long",
    "messages": [
      {
        "role": "user",
        "content": "What are the working hours according to the employee handbook?"
      }
    ]
  }'

# 返回结果
{"id":"e856547d-4b5c-9e9a-a61b-94857327626e","choices":[{"index":0,"message":{"role":"assistant",
"content":"**References:**\n[1] [Attendance Policy](https://guidelines.ai/handbook/4334)\n\nThe working hours specified 
in the employee handbook are from 9:00 AM to 6:00 PM, which includes a lunch break from 12:30 PM to 1:30 PM 
[1]."},"finish_reason":"stop"}],"created":1740926279,"model":"qwen-long","object":"chat.completion","usage":
{"prompt_tokens":567,"completion_tokens":47,"total_tokens":614}}
```
