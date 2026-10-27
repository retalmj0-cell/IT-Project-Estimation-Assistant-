import json
from mcp.server.fastmcp import FastMCP
from mcp_server.calculations import (
    PERT_RULES, CONTINGENCY_RATES, AGILE_SPRINT_RULES,
    calculate_pert, calculate_budget, calculate_sprint
)

mcp = FastMCP("Project Estimator MCP Server")

@mcp.tool()
def pert_tool(optimistic: float, most_likely: float, pessimistic: float) -> dict:
    """Calculate expected task duration using PERT formula."""
    return calculate_pert(optimistic, most_likely, pessimistic)

@mcp.tool()
def budget_tool(hours: float, hourly_rate: float, contingency_percent: float) -> dict:
    """Calculate project cost including base labor and contingency reserve."""
    return calculate_budget(hours, hourly_rate, contingency_percent)

@mcp.tool()
def sprint_tool(team_size: int, days: int, focus_factor: float) -> dict:
    """Calculate total available team hours in an agile sprint."""
    return calculate_sprint(team_size, days, focus_factor)

@mcp.resource("project://pert/formula-rules")
def pert_rules() -> str:
    """Rules and formula for PERT estimation."""
    return json.dumps(PERT_RULES)

@mcp.resource("project://budget/contingency-rates")
def contingency_rates() -> str:
    """Standard contingency rates for project budgeting."""
    return json.dumps(CONTINGENCY_RATES)

@mcp.resource("project://agile/sprint-rules")
def sprint_rules() -> str:
    """Rules for calculating agile sprint capacity."""
    return json.dumps(AGILE_SPRINT_RULES)

@mcp.prompt()
def pert_assistant_prompt() -> str:
    """Workflow for the PERT estimation specialist."""
    return "Check optimistic, most_likely, and pessimistic values. Read PERT rules. Call pert_tool."

@mcp.prompt()
def budget_assistant_prompt() -> str:
    """Workflow for the budget specialist."""
    return "Check hours, hourly_rate, and contingency_percent. Read contingency rates. Call budget_tool."

@mcp.prompt()
def sprint_assistant_prompt() -> str:
    """Workflow for the sprint capacity specialist."""
    return "Check team_size, days, and focus_factor. Read sprint rules. Call sprint_tool."

if __name__ == "__main__":
    mcp.run(transport="stdio")