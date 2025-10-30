"""Markdown documentation generator."""


def generate_deterministic_markdown_spec(
  analysis: dict,
  spec_type: str = "public",
) -> str:
  """Generate deterministic markdown documentation from analysis."""
  if "error" in analysis:
    return f"# Error\n\n{analysis['error']}\n"

  lines = []
  lines.append(f"# {analysis['module_name']}")
  lines.append("")

  # Module-level information
  if analysis.get("docstring"):
    lines.append(analysis["docstring"])
    lines.append("")

  # Module comments (already sorted)
  if analysis.get("module_comments"):
    lines.append("## Module Notes")
    lines.append("")
    for comment in analysis["module_comments"]:
      lines.append(f"- {comment}")
    lines.append("")

  # Constants (already sorted)
  if analysis.get("constants"):
    constants_to_show = analysis["constants"]
    if spec_type == "public":
      constants_to_show = [c for c in constants_to_show if not c["is_private"]]

    if constants_to_show:
      lines.append("## Constants")
      lines.append("")
      for const in constants_to_show:
        type_info = f": {const['type']}" if const.get("type") else ""
        comment_info = f" - {const['comment']}" if const.get("comment") else ""
        lines.append(f"- `{const['name']}{type_info}`{comment_info}")
      lines.append("")

  # Functions (already sorted)
  if analysis.get("functions"):
    functions_to_show = analysis["functions"]
    if spec_type == "public":
      functions_to_show = [f for f in functions_to_show if not f["is_private"]]

    if functions_to_show:
      lines.append("## Functions")
      lines.append("")
      for func in functions_to_show:
        args_str = ", ".join(func["args"])
        return_type = f" -> {func['return_type']}" if func.get("return_type") else ""
        signature = f"{func['name']}({args_str}){return_type}"

        decorators = ""
        if func.get("decorators"):
          decorators = " ".join([f"@{dec}" for dec in func["decorators"]]) + " "

        docstring_info = f": {func['docstring']}" if func.get("docstring") else ""
        comment_info = f" - {func['comment']}" if func.get("comment") else ""

        lines.append(
          f"- {decorators}`{signature}`{docstring_info}{comment_info}",
        )
      lines.append("")

  # Classes (already sorted)
  if analysis.get("classes"):
    classes_to_show = analysis["classes"]
    if spec_type == "public":
      classes_to_show = [c for c in classes_to_show if not c["is_private"]]

    for class_info in classes_to_show:
      lines.append("## Classes")
      lines.append("")
      break

    for class_info in classes_to_show:
      lines.append(f"### {class_info['name']}")
      lines.append("")

      if class_info.get("docstring"):
        lines.append(class_info["docstring"])
        lines.append("")

      # Class comment
      if class_info.get("comment"):
        lines.append(f"*{class_info['comment']}*")
        lines.append("")

      # Base classes
      if class_info.get("bases"):
        lines.append(f"**Inherits from:** {', '.join(class_info['bases'])}")
        lines.append("")

      # Methods (already sorted within class)
      methods_to_show = class_info["methods"]
      if spec_type == "public":
        methods_to_show = [m for m in methods_to_show if not m["is_private"]]

      if methods_to_show:
        lines.append("#### Methods")
        lines.append("")

        for method in methods_to_show:
          args_str = ", ".join(method["args"])
          return_type = (
            f" -> {method['return_type']}" if method.get("return_type") else ""
          )
          signature = f"{method['name']}({args_str}){return_type}"

          decorators = ""
          if method.get("decorators"):
            decorators = " ".join([f"@{dec}" for dec in method["decorators"]]) + " "

          docstring_info = f": {method['docstring']}" if method.get("docstring") else ""
          comment_info = f" - {method['comment']}" if method.get("comment") else ""

          lines.append(
            f"- {decorators}`{signature}`{docstring_info}{comment_info}",
          )

        lines.append("")

  return "\n".join(lines)
