from chatbot.services.mcp_client import ProjectMCPClient

class BaseAgent:
    name = ""
    tool_name = ""
    resource_uri = ""
    prompt_name = ""
    required_fields = ()

    def __init__(self):
        self.mcp = ProjectMCPClient()

    async def execute(self, parameters: dict) -> dict:
        missing = [key for key in self.required_fields if parameters.get(key) is None or parameters.get(key) == ""]
        if missing:
            return {
                "agent": self.name,
                "status": "missing_information",
                "missing_fields": missing,
                "message": "Please provide: " + ", ".join(missing),
            }

        arguments = {key: parameters[key] for key in self.required_fields}
        try:
            result = await self.mcp.execute(
                tool_name=self.tool_name,
                arguments=arguments,
                resource_uri=self.resource_uri,
                prompt_name=self.prompt_name,
            )
        except Exception as e:
            return {
                "agent": self.name,
                "status": "error",
                "message": str(e),
            }

        data = result["tool_result"]
        if "error" in data:
            return {
                "agent": self.name,
                "status": "validation_error",
                "message": data["error"],
                "data": data,
                "mcp": self._mcp_info(result),
            }

        return {
            "agent": self.name,
            "status": "success",
            "message": self.format_result(data),
            "data": data,
            "mcp": self._mcp_info(result),
        }

    def _mcp_info(self, result):
        return {
            "tool": self.tool_name,
            "resource": result["resource"],
            "prompt": result["prompt"],
        }

    def format_result(self, data: dict) -> str:
        raise NotImplementedError

class PertAgent(BaseAgent):
    name = "pert_agent"
    tool_name = "pert_tool"
    resource_uri = "project://pert/formula-rules"
    prompt_name = "pert_assistant_prompt"
    required_fields = ("optimistic", "most_likely", "pessimistic")

    def format_result(self, data):
        return f"Expected Duration: {data['expected_duration']} units (Std Dev: {data['standard_deviation']})."

class BudgetAgent(BaseAgent):
    name = "budget_agent"
    tool_name = "budget_tool"
    resource_uri = "project://budget/contingency-rates"
    prompt_name = "budget_assistant_prompt"
    required_fields = ("hours", "hourly_rate", "contingency_percent")

    def format_result(self, data):
        return f"Base Cost: {data['base_cost']}, Total Budget: {data['total_budget']} {data['unit']}."

class SprintAgent(BaseAgent):
    name = "sprint_agent"
    tool_name = "sprint_tool"
    resource_uri = "project://agile/sprint-rules"
    prompt_name = "sprint_assistant_prompt"
    required_fields = ("team_size", "days", "focus_factor")

    def format_result(self, data):
        return f"Total Available Sprint Capacity: {data['total_available_capacity_hours']} hours."