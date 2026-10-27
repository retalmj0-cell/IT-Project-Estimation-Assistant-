from chatbot.agents.specialists import PertAgent, BudgetAgent, SprintAgent


class SupervisorAgent:
    def __init__(self):
        self.agents = {
            "pert_agent": PertAgent(),
            "budget_agent": BudgetAgent(),
            "sprint_agent": SprintAgent(),
        }

    def select_agent(self, message: str, requested_agent=None):
        if requested_agent is not None:
            return requested_agent if requested_agent in self.agents else None

        text = message.lower()
        if any(word in text for word in ("pert", "duration", "time", "schedule", "task")):
            return "pert_agent"
        if any(word in text for word in ("budget", "cost", "price", "money", "labor")):
            return "budget_agent"
        if any(word in text for word in ("sprint", "capacity", "points", "agile", "team")):
            return "sprint_agent"
        return None

    async def process(self, message: str, parameters: dict, requested_agent=None) -> dict:
        name = self.select_agent(message, requested_agent)
        if name is None:
            return {
                "agent": "supervisor",
                "status": "unsupported",
                "message": "Choose pert_agent, budget_agent, or sprint_agent.",
            }
        return await self.agents[name].execute(parameters)