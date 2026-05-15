import json
from sqlalchemy.orm import Session
from app.core.gateway.router import GatewayRouter
from app.core.gateway.call_logger import CallLogger

LLM_SCORER_PROMPT = """\u4f60\u662f\u4e00\u4e2a\u4f01\u4e1a\u5339\u914d\u8bc4\u4f30\u4e13\u5bb6\u3002\u8bf7\u6839\u636e\u4ee5\u4e0b\u4fe1\u606f\uff0c\u8bc4\u4f30\u9700\u6c42\u65b9\u4e0e\u5019\u9009\u4f01\u4e1a\u7684\u5339\u914d\u5ea6\u3002

## \u7528\u6237\u9700\u6c42
{requirement}

## \u5019\u9009\u4f01\u4e1a
- \u540d\u79f0: {company_name}
- \u884c\u4e1a: {industry}
- \u89c4\u6a21: {scale}
- \u63cf\u8ff0: {description}

## \u5df2\u6709\u5339\u914d\u6570\u636e
- \u6807\u7b7e\u91cd\u5408\u5ea6: {tag_score:.1f}/100
- \u8bed\u4e49\u76f8\u4f3c\u5ea6: {semantic_score:.1f}/100
- \u4e1a\u52a1\u89c4\u5219\u5f97\u5206: {rule_score:.1f}/100

\u8bf7\u7ed9\u51fa:
1. \u7efc\u5408\u5339\u914d\u5ea6\u5f97\u5206 (0-100)
2. \u7f6e\u4fe1\u5ea6 (high/medium/low)
3. \u7b80\u77ed\u7684\u81ea\u7136\u8bed\u8a00\u89e3\u91ca (100\u5b57\u4ee5\u5185)

\u4ee5JSON\u683c\u5f0f\u8fd4\u56de: {{\"score\": 85, \"confidence\": \"high\", \"explanation\": \"...\"}}"""

class LLMScorer:
    def __init__(self, db: Session):
        self.db = db
        self.router = GatewayRouter()

    async def score(self, requirement: str, company: dict,
                    tag_score: float, semantic_score: float,
                    rule_score: float) -> dict:
        prompt = LLM_SCORER_PROMPT.format(
            requirement=requirement,
            company_name=company.get("name", ""),
            industry=company.get("industry", ""),
            scale=company.get("scale", ""),
            description=company.get("description", ""),
            tag_score=tag_score,
            semantic_score=semantic_score,
            rule_score=rule_score,
        )

        resp, provider, adapter = await self.router.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="qwen-turbo",
            temperature=0.1,
        )

        # Log the call
        usage = resp.get("usage", {})
        logger = CallLogger(self.db, provider, "qwen-turbo")
        logger.start()
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        logger.set_usage(prompt_tokens, completion_tokens)
        cost = adapter.estimate_cost(prompt_tokens, completion_tokens, "qwen-turbo")
        logger.log(cost)

        content = resp["choices"][0]["message"]["content"].strip()
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            result = {"score": 0, "confidence": "low", "explanation": "\u8bc4\u5206\u5931\u8d25"}
        return result
