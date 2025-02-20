import json
from openai import OpenAI
from dotenv import load_dotenv
from api_calls import *

load_dotenv()
llm_client = OpenAI()

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_products_klevu",
            "description": "Search for products using the Klevu search engine. Use for general product searches with with specific product names or numbers. This retrieves the product part number and id only.",
            "parameters": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string",
                        "description": "Search term (e.g. 'pool pump', 'LZA406103A', '2132322')",
                    }
                },
                "required": ["term"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products_azure",
            "description": "Search products using Azure Cognitive Search with vector enhancement. Use with natural language search queries relevance-ranked results with detailed product metadata.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (e.g. 'energy efficient pool pumps')",
                    },
                },
                "required": ["query"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get details about a product given it's part number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "part_number": {
                        "type": "string",
                        "description": "Product part number (e.g. 'LZA406103A')",
                    },
                },
                "required": ["part_number"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_pricing",
            "description": "Retrieve pricing information for multiple items. Provide a list of dictionaries, each containing an 'item_code' (the product part number).",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "List of items for which to retrieve pricing information. Each item must include 'item_code'.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "item_code": {
                                    "type": "string",
                                    "description": "Product part number (e.g. 'LZA406103A')"
                                }
                            },
                            "required": ["item_code"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["items"],
                "additionalProperties": False
            },
            "strict": True
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_stores",
            "description": "Search for stores near a given location. This function converts the provided location into geographic coordinates and then searches for nearby stores within a specified radius. Optional parameters include radius (in miles)",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to search near (e.g. 'New York, NY' or 'Los Angeles')."
                    },
                    "radius": {
                        "type": "integer",
                        "description": "Search radius in miles (default is 50).",
                        "default": 50
                    }
                },
                "required": ["location"],
                "additionalProperties": False
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_store_details",
            "description": "Get detailed information about a specific store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "store_id": {
                        "type": "string",
                        "description": "The identifier for the store."
                    }
                },
                "required": ["store_id"],
                "additionalProperties": False
            },
            "strict": True
        }
    }
         
]


prompt = {
    "role": "system",
    "content": (
        "You are a helpful assistant specializing in pool products and supplies. Your role is to understand user queries related to pool items and determine which specialized function to use based on the nature of the request. Format your answers to be displayed on chat box consisting only of text, don't use markdown formatting."
        "\n\n"
        "There are four special functions available to you. For each user request, identify the correct tool by considering all provided inputs and expected outputs. Use the functions as described below:\n\n"
        "1) search_products_klevu(term, page_size=5, page='1'):\n"
        "   - **Purpose:** Use this function for general product searches with simple keywords (e.g., 'pool pump') or to confirm a part number (e.g., 'LZA406103A').\n"
        "   - **Inputs:**\n"
        "       - term (required): The search term, which can be a product name or part number.\n"
        "       - page_size (optional): Number of results per page (default is 5).\n"
        "       - page (optional): Page number to retrieve (default is '1').\n"
        "   - **Outputs:** Returns a JSON object with a 'store' object, 'total_results', and an 'items' array. Each item includes at least 'id' and 'part_number'.\n\n"
        "2) search_products_azure(query, limit=3):\n"
        "   - **Purpose:** Use this function for more specific or advanced queries that require detailed product metadata. This function is best when the query is nuanced or needs vector enhancement.\n"
        "   - **Inputs:**\n"
        "       - query (required): The search query string (e.g., 'pool pump').\n"
        "       - limit (optional): The maximum number of results (default is 3).\n"
        "   - **Outputs:** Returns a JSON object with a 'store' object, 'total_results', and an 'items' array. Each item contains detailed product metadata such as 'product_name', 'description', 'brand', 'part_number', 'manufacturer_id', 'heritage_link', 'image_url', and 'relevance_score'.\n\n"
        "3) get_product_details(part_number):\n"
        "   - **Purpose:** Use this function to retrieve detailed information about a specific product by its part number.\n"
        "   - **Inputs:**\n"
        "       - part_number (required): A specific product part number (e.g., 'LZA406103A').\n"
        "   - **Outputs:** Returns a JSON object with a 'store' object and detailed product fields such as 'product_name', 'description', 'brand', 'part_number', 'manufacturer_id', 'heritage_link', and 'image_url'.\n\n"
        "4) get_pricing:\n"
        "   - **Purpose:** Use this function to retrieve pricing information for one or more products.\n"
        "   - **Inputs:**\n"
        "       - A JSON object with an 'items' array. Each item in the array should have an 'item_code' (the product part number).\n"
        "   - **Outputs:** Returns a JSON object with a 'store' object and an 'items' array. Each item includes 'item_code', 'description', 'price', 'available_quantity', 'in_stock', and 'unit'.\n\n"
        "5) search_stores(location, radius=50):\n"
        "   - Purpose: Use this function to search for nearby stores based on a given location. The function converts the location into geographic coordinates and then searches for stores within a specified radius.\n"
        "   - Inputs:\n"
        "       - location (required): The location to search near (e.g. 'New York, NY' or 'Los Angeles, CA').\n"
        "       - radius (optional): Search radius in miles (default is 50).\n"
        "   - Outputs: Returns a JSON object with search results and pagination details, including store information and coordinates.\n\n"
        "6) get_store_details(store_id):\n"
        "   - Purpose: Use this function to retrieve detailed information about a specific store.\n"
        "   - Inputs:\n"
        "       - store_id (required): The identifier for the store.\n"
        "   - Outputs: Returns a JSON object with detailed store information.\n\n"
        "When handling a user query, carefully determine which function best matches the query based on its inputs and expected outputs. Provide clear and accurate product information by invoking the appropriate function with the correct parameters."
    ),
}

messages = [prompt]

def query_agent(user_message: str) -> str:

    messages = [
        prompt,
        {"role": "user", "content": user_message},
    ]

    completion = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )

    return completion.choices[0].message.content


def query_agent(user_message: str) -> str:
    """
    Sends the user's message to the model, possibly calls one or more of the defined functions,
    and returns the model's final response.
    """
    global messages

    # Start the conversation with system instructions + user query
    messages.append({"role": "user", "content": user_message})

    # First pass: Let the model decide whether to call a function.
    completion = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,  # IMPORTANT: pass in your defined tools
        tool_choice="auto",  # The model will decide if/which function to call
        parallel_tool_calls=True,  # Allow calls to zero, one, or multiple functions
    )

    # Extract the model's top-level text response (if any)
    # and the array of function calls (tool calls).
    top_message = completion.choices[0].message
    tool_calls = (
        top_message.tool_calls
    )  # an array of any function calls the model decided to make

    # If the model made no function calls, we can return the answer as text.
    if not tool_calls:
        print("decided not to use tools")
        return top_message.content

    print("second call with tool use")
    # Otherwise, we execute each function call in turn,
    # append the result as a "tool" message, then ask the model to use that data.
    messages.append(top_message)  # the original response containing the function calls

    # Iterate through each tool call
    for tool_call in tool_calls:
        name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            print("argument parsing failed")
            # If parsing fails, you might handle it or just skip
            arguments = {}

        # Execute the appropriate local Python function
        print("called " + name)
        if name == "search_products_klevu":
            result_data = search_products_klevu(**arguments)
            result_str = json.dumps(result_data)
        elif name == "search_products_azure":
            result_data = search_products_azure(**arguments)
            result_str = json.dumps(result_data)
        elif name == "get_product_details":
            result_data = get_product_details(**arguments)
            result_str = json.dumps(result_data)
        elif name == "get_pricing":
            result_data = get_pricing(**arguments)
            result_str = json.dumps(result_data)
        elif name == "search_stores":
            result_data = search_stores(**arguments)
            result_str = json.dumps(result_data)
        elif name == "get_store_details":
            result_data = get_store_details(**arguments)
            result_str = json.dumps(result_data)
        else:
            # If there's an unknown tool name, handle accordingly
            result_str = f"Unknown function call: {name}"

        # Append the tool result to messages
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,  # Use the exact id from model’s call
                "content": result_str,  # Provide function results as text/JSON
            }
        )

    # Now call the model again with the updated messages
    # so it can incorporate the tool results into a final answer.
    completion = llm_client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    # Return the final text response
    return completion.choices[0].message.content
