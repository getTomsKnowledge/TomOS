# tomos/kernel.py
from openai import OpenAI
# Now you can import modules from the parent directory
from tomos.utils import prompt_file_parser, response #, streaming

# The main TomOS class, which manages modes, templates, and API calls:
class TomOS:
    
    # Constructor with parameters for prompt, client, model, mode, template usage, local files, streaming, and dry run:
    def __init__(self, prompt: str = "This is a test.", client: OpenAI=OpenAI(), model: str = "gpt-4o-mini", mode: str = "", template: bool = False, local: bool = True, stream: bool = False, dry: bool = True, schema: str = "free"):
        self.client = client # OpenAI client object
        self.model = model # gpt-4o, gpt-4o-mini
        self.mode = mode # career, growth, play
        self.local = local # Use local files for context variables
        self.template = template # Use template file for context variables
        self.stream = stream # Stream responses from the API in real-time
        self.vars = {} # Dictionary to hold user-defined variables for templates
        self.templateFilepath = -1  # Placeholder for the template file object
        self.system = "" # System prompt context, to be set by mode module
        self.userPrompt = prompt # User prompt
        self.dry = dry # If True, skip API call and just print prompt
        self.schema = schema # If set, use schema for structured output
        self.output_schema = None # Placeholder for schema output format
        self.schema_filepath = None # Placeholder for schema file path
        self.output_text = None # Placeholder for API output text
        self.usage = None # Placeholder for API usage stats

    # Internal method to manage template files and variables:
    def template_manager(self):
        # Get list of available templates in selected mode:
        templateList = prompt_file_parser.get_filenames_from_folder(self.mode)
        print(f'Available templates in {self.mode} include:\n\n {templateList}\n\n')
        templateName = input("Please enter the desired template\'s filename: \n")
        prompt_file_parser.set_template_file(self, templateName)
        self.vars = prompt_file_parser.read_kv_block(self)
        for i in self.vars:
            self.vars[i] = input(f'Please input a value for {i}: ')
            print(f'Setting variable {i} to value {self.vars[i]}.\n')
        # Get prompt text from template file:
        self.userPrompt = prompt_file_parser.read_prompt(self)

        # Format user prompt with template variables:
        print(f'Formatting prompt with variables: {self.vars}\n')       
        formattedPrompt = self.userPrompt.format(**self.vars)
        self.userPrompt = formattedPrompt
        return

    # Internal method to call the OpenAI API:
    def _call(self) -> str:       
        print(f'\n\nCalling OpenAI API with prompt:\n    {self.userPrompt}\n\n')
        if self.dry:
            print('Dry run enabled. No API call was made. Your prompt was:\n\n')
            return self.userPrompt
        else:
            return response.responses_call(self)

    # Career, an aerospace systems engineering and astrodynamics assistant:
    def career(self) -> str:
        self.system = (
            "You are a career co-pilot for an aerospace systems engineer and astrodynamicist. "
            "Be precise, structured, and helpful with SysML, RFPs, and astrodynamics context."
        )
        if (self.template):
            self.template_manager()
        return self._call()

    # Growth, a multilingual tutor and research scribe:
    def growth(self) -> str:
        self.system = (
            "You are a multilingual tutor and research scribe. "
            "Explain clearly, give examples, and propose short exercises."
        )
        if (self.template):
            self.template_manager()
        return self._call()

    # Play, a creative engine for sci-fi, poetry, and music theory toys:
    def play(self) -> str:
        self.system = (
            "You are a creative engine for sci‑fi, poetry, and music theory toys. "
            "Be imaginative but crisp."
        )
        if (self.template):
            self.template_manager()
        return self._call()