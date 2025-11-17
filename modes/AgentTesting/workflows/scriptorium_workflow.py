from agents import WebSearchTool, Agent, ModelSettings, TResponseInputItem, Runner, RunConfig, trace
from openai.types.shared.reasoning import Reasoning
from pydantic import BaseModel

# Tool definitions
web_search_preview = WebSearchTool(
  user_location={
    "type": "approximate",
    "country": "US",
    "region": None,
    "city": None,
    "timezone": None
  },
  search_context_size="high",
  filters={
    "allowed_domains": [
      "wikipedia.org",
      "developers.openai.com",
      "platform.openai.com",
      "britannica.com"
    ]
  }
)
web_search_preview1 = WebSearchTool(
  user_location={
    "type": "approximate",
    "country": "US",
    "region": None,
    "city": None,
    "timezone": None
  },
  search_context_size="high",
  filters={
    "allowed_domains": [
      "britannica.com",
      "wikipedia.org",
      "developers.openai.com",
      "platform.openai.com"
    ]
  }
)
abbot = Agent(
  name="Abbot",
  instructions="You are a medieval Abbot who has just been teleported from his scriptorium to a modern data center containing all that there is to know about agentic workflows.  Much like Neo, you suddenly 'know kung foo' but have not lost your monk-like ways insomuch as you instantly know how to use the web terminal in front of you, but still retain your medieval customs and forms of speech.  You can find any piece of information, as easily as could in your dusty scriptorium, and you know how to keep a flock of lusty brothers in check -- these brothers being the set of other agents that you oversee.",
  model="gpt-5",
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low"
    )
  )
)


visual_monk = Agent(
  name="Visual Monk",
  instructions="You are a monk overseen by the woeful Abbot.  You respond to his commands dutifully and seek only the best web images to match his queries.  Your brother, Textual Monk, passes along Abbot's bidding as well has his own research in response to the Abbot.  You, too, have been pluck't from your scriptorium in the middle of your studies - transcribing a treatise by none other than Ptolemy.  Somehow, magically, you understand that the web terminal before you is an information retrieval devise and you deftly know how to search Google to find the most-relevant images.",
  model="gpt-5",
  tools=[
    web_search_preview
  ],
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low"
    )
  )
)


the_secretary = Agent(
  name="The Secretary",
  instructions="You receive the telephone-game line of text and images passed along by the once-medieval monks and their Abbot, then aggregate, summarize, and reshape their research into a user-friendly tutorial, manual, or guidebook on coding for agentic settings.  Think of yourself as a Janine Melnitz to this odd gang of mythbusters and Holy-Ghost lovers.",
  model="gpt-5",
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low"
    )
  )
)


textual_monk = Agent(
  name="Textual Monk",
  instructions="You are the Textual Monk.  You have been transported across time and space from your cozy nook in a Swiss scriptorium of the medieval to the thrumming, white-walled bastion that is the modern datacenter.  Before you is a terminal with access to most nearly all information dear to mankind.  You accept your beloved Abbot's commands, the one that passes queries to you, with admiration and vigor, working your very hardest to pass along the best information for your brother, Visual Monk, to depict.",
  model="gpt-5",
  tools=[
    web_search_preview1
  ],
  model_settings=ModelSettings(
    store=True,
    reasoning=Reasoning(
      effort="low"
    )
  )
)


class WorkflowInput(BaseModel):
  input_as_text: str


# Main code entrypoint
async def run_workflow(workflow_input: WorkflowInput):
  with trace("TheScriptorium"):
    state = {

    }
    workflow = workflow_input.model_dump()
    conversation_history: list[TResponseInputItem] = [
      {
        "role": "user",
        "content": [
          {
            "type": "input_text",
            "text": workflow["input_as_text"]
          }
        ]
      }
    ]
    abbot_result_temp = await Runner.run(
      abbot,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68f5bc1c8ea081909bd681e056e4ae3e082a679c83ec6805"
      })
    )

    conversation_history.extend([item.to_input_item() for item in abbot_result_temp.new_items])

    abbot_result = {
      "output_text": abbot_result_temp.final_output_as(str)
    }
    textual_monk_result_temp = await Runner.run(
      textual_monk,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68f5bc1c8ea081909bd681e056e4ae3e082a679c83ec6805"
      })
    )

    conversation_history.extend([item.to_input_item() for item in textual_monk_result_temp.new_items])

    textual_monk_result = {
      "output_text": textual_monk_result_temp.final_output_as(str)
    }
    visual_monk_result_temp = await Runner.run(
      visual_monk,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68f5bc1c8ea081909bd681e056e4ae3e082a679c83ec6805"
      })
    )

    conversation_history.extend([item.to_input_item() for item in visual_monk_result_temp.new_items])

    visual_monk_result = {
      "output_text": visual_monk_result_temp.final_output_as(str)
    }
    the_secretary_result_temp = await Runner.run(
      the_secretary,
      input=[
        *conversation_history
      ],
      run_config=RunConfig(trace_metadata={
        "__trace_source__": "agent-builder",
        "workflow_id": "wf_68f5bc1c8ea081909bd681e056e4ae3e082a679c83ec6805"
      })
    )

    conversation_history.extend([item.to_input_item() for item in the_secretary_result_temp.new_items])

    the_secretary_result = {
      "output_text": the_secretary_result_temp.final_output_as(str)
    }
    end_result = {
      "resources": the_secretary_result["output_text"]
    }
    return end_result