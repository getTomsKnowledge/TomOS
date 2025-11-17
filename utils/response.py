# tomos/utils/response.py
from . import prompt_file_parser
import time

# A module to handle API response calls, including streaming support.
def responses_call(thisOS: object) -> str:

    stats = {}
    error = None

    import json

    # Load and prepare schema if needed
    text_param = None
    if thisOS.schema and thisOS.schema != "free" and thisOS.model.startswith("gpt-5"):
        schema_dict = prompt_file_parser.select_and_load_json_schema(thisOS.mode)
        text_param = {
            "format": {
                "type": "json_schema",
                "name": f"{thisOS.mode}_response",
                "schema": schema_dict,
                "strict": True
            }
        }
        print(f'Using JSON schema for structured output:\n{json.dumps(schema_dict, indent=2)}\n\n')

    # Prepare input as a list of messages
    input_messages = [
        {"role": "system", "content": thisOS.system},
        {"role": "user", "content": thisOS.userPrompt}
    ]

    print(f'\n\nCalling OpenAI API with prompt:\n    {thisOS.userPrompt}\n\n')
    start_time = time.time()
    response = thisOS.client.responses.create(
        model=thisOS.model,
        input=input_messages,
        stream=thisOS.stream,
        text=text_param
    )
    if not thisOS.stream:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"API non-streaming call completed in {elapsed_time:.2f} seconds.\n")

    try:
        thisOS.output_text = response.output_text
        # Usage stats (if available)
        usage = getattr(response, "usage", None)
        if usage:
            stats["input_tokens"] = getattr(usage, "input_tokens", None)
            stats["output_tokens"] = getattr(usage, "output_tokens", None)
            stats["total_tokens"] = getattr(usage, "total_tokens", None)
            stats["model"] = thisOS.model
            thisOS.usage = stats
        else:
            print("No usage stats available in response.\n\n")
            # stats["input_tokens"] = stats["output_tokens"] = stats["total_tokens"] = None
    except Exception as e:
        output_text = ""
        error = str(e)
        print(f"Error extracting output text: {error}\n\n")

    # If streaming, handle the stream:
    if thisOS.stream:
        collected_text_chunks = []
        for chunk in response:
            # Check if the chunk has data containing the text delta
            if hasattr(chunk, 'type') and chunk.type == 'response.output_text.delta':
                text_chunk = chunk.delta
                collected_text_chunks.append(text_chunk)
                print(text_chunk, end="", flush=True)  # Print the text incrementally

        print("\n\n")  # ensure we end with a newline
        return ''.join(collected_text_chunks)
    if thisOS.stream:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"API streaming call completed in {elapsed_time:.2f} seconds.\n")

    mean_tokens = 1e6
    mean_input_cost_gpt5 = 2.5 # $2.50 per 1M tokens input
    mean_output_cost_gpt5 = 10.0 # $10.00 per 1M tokens
    normalized_input = stats.get("input_tokens", 1)/mean_tokens
    input_cost = normalized_input * mean_input_cost_gpt5
    stats["input_cost"] = f"${input_cost:,.2f}"
    normalized_output = stats.get("output_tokens", 1)/mean_tokens
    output_cost = normalized_output * mean_output_cost_gpt5
    stats["output_cost"] = f"${output_cost:,.2f}"
    stats["total_cost"] = f"${(input_cost + output_cost):,.2f}"
    thisOS.usage = stats

    # Print final output and stats:
    print('============================================================================\n')
    print('============================================================================\n')
    print(f'Output text:\n{thisOS.output_text}\n\n')
    print('============================================================================\n')
    print('============================================================================\n')
    print(f'API call complete. Usage stats: {thisOS.usage}\n')
    print('============================================================================\n')
    print('============================================================================\n')
    print(f'Full response object:\n{response}\n\n')
    print('============================================================================\n')
    print('============================================================================\n')

    return