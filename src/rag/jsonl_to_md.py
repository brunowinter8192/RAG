# INFRASTRUCTURE
import argparse
import json
import re
from pathlib import Path


# ORCHESTRATOR
def convert_workflow(jsonl_path: str, output_path: str) -> int:
    messages = load_jsonl(jsonl_path)
    tool_calls = extract_tool_calls(messages)
    md_content = format_as_markdown(tool_calls)
    write_output(output_path, md_content)
    return len(tool_calls)


# FUNCTIONS

# Load all lines from JSONL file
def load_jsonl(jsonl_path: str) -> list[dict]:
    path = Path(jsonl_path)
    if not path.exists():
        raise FileNotFoundError(f"JSONL not found: {jsonl_path}")

    messages = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return messages


# Extract tool_use and tool_result pairs from messages
def extract_tool_calls(messages: list[dict]) -> list[dict]:
    tool_use_cache = {}
    tool_calls = []

    for message in messages:
        content_blocks = get_content_blocks(message)
        if not content_blocks:
            continue

        for block in content_blocks:
            if block.get('type') == 'tool_use':
                tool_data = {
                    'tool_name': block.get('name', 'Unknown'),
                    'input': block.get('input', {}),
                    'output': None,
                    'tool_use_id': block.get('id', ''),
                    'timestamp': message.get('timestamp', '')
                }
                tool_use_cache[tool_data['tool_use_id']] = tool_data

            elif block.get('type') == 'tool_result':
                tool_use_id = block.get('tool_use_id')
                if tool_use_id in tool_use_cache:
                    tool_data = tool_use_cache[tool_use_id]
                    tool_data['output'] = extract_result_content(block)
                    tool_calls.append(tool_data)
                    del tool_use_cache[tool_use_id]

    return sorted(tool_calls, key=lambda x: x.get('timestamp', ''))


# Get content blocks from message (handles nested structures)
def get_content_blocks(message: dict) -> list[dict]:
    if 'message' in message and isinstance(message['message'], dict):
        content = message['message'].get('content', [])
    else:
        content = message.get('content', [])

    if isinstance(content, list):
        return content
    return []


# Extract text content from tool_result block
def extract_result_content(block: dict) -> str:
    content = block.get('content', '')
    if isinstance(content, list) and len(content) > 0:
        if isinstance(content[0], dict):
            text = content[0].get('text', '')
        else:
            text = str(content[0])
    else:
        text = str(content)

    return strip_system_reminders(text)


# Remove system-reminder tags from content
def strip_system_reminders(content: str) -> str:
    pattern = r'<system-reminder>.*?</system-reminder>'
    return re.sub(pattern, '', content, flags=re.DOTALL).strip()


# Format tool calls as Markdown (--- separator for chunking)
def format_as_markdown(tool_calls: list[dict]) -> str:
    sections = []

    for call in tool_calls:
        section = format_tool_call(call)
        sections.append(section)

    return '\n\n---\n\n'.join(sections)


# Format single tool call as Markdown section
def format_tool_call(call: dict) -> str:
    tool_name = call['tool_name']
    input_data = call['input']
    output = call['output'] or '(no output)'

    input_str = format_input(input_data)

    return f"""# Tool: {tool_name}

**Input:**
{input_str}

**Output:**
{output}"""


# Format input dict as readable string
def format_input(input_data: dict) -> str:
    if not input_data:
        return '(no input)'

    if not isinstance(input_data, dict):
        return str(input_data)

    parts = []
    for key, value in input_data.items():
        value_str = str(value)
        if len(value_str) > 500:
            value_str = value_str[:500] + '...'
        parts.append(f"- {key}: {value_str}")

    return '\n'.join(parts)


# Write content to output file
def write_output(output_path: str, content: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Claude Code JSONL to Markdown")
    parser.add_argument("--input", required=True, help="Path to JSONL file")
    parser.add_argument("--output", required=True, help="Path for output MD file")

    args = parser.parse_args()
    count = convert_workflow(args.input, args.output)
    print(f"Converted {count} tool calls to {args.output}")
