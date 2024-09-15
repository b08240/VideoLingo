import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.ask_gpt import ask_gpt
from core.prompts_storage import generate_shared_prompt, get_prompt_faithfulness, get_prompt_expressiveness

def translate_lines(lines, previous_content_prompt, after_cotent_prompt, things_to_note_prompt, summary_prompt, index = 0):
    from config import step4_2_translate_direct_model, step4_2_translate_free_model
    
    shared_prompt = generate_shared_prompt(previous_content_prompt, after_cotent_prompt, summary_prompt, things_to_note_prompt)

    # Retry translation if the length of the original text and the translated text are not the same, or if the specified key is missing
    def retry_translation(prompt, model, step_name, valide_key=None, valid_sub_key=None):
        for retry in range(3):
            result = ask_gpt(prompt + retry*" ", model=model, response_json=True, valid_key=valide_key, valid_sub_key=valid_sub_key, log_title=f'translate_{step_name}')
            if len(lines.split('\n')) == len(result):
                return result
            if retry != 2:
                print(f'⚠️ {step_name.capitalize()} translation of block {index} failed, Retry...')
        raise ValueError(f'❌ {step_name.capitalize()} translation of block {index} failed after 3 retries. Please check your input text.')

    ## Step 1: Faithful to the Original Text
    prompt1 = get_prompt_faithfulness(lines, shared_prompt)
    faith_result = retry_translation(prompt1, step4_2_translate_direct_model, 'faithfulness', valide_key="1", valid_sub_key="Direct Translation")

    for i in faith_result:
        faith_result[i]["Direct Translation"] = faith_result[i]["Direct Translation"].replace('\n', ' ')

    ## Step 2: Express Smoothly  
    prompt2 = get_prompt_expressiveness(faith_result, lines, shared_prompt)
    express_result = retry_translation(prompt2, step4_2_translate_free_model, 'expressiveness', valide_key="1", valid_sub_key="Free Translation")

    for i in express_result:
        print(f'📄 Original Subtitle:   {faith_result[i]["Original Subtitle"]}')
        print(f'📚 Direct Translation:  {faith_result[i]["Direct Translation"]}')
        print(f'🧠 Free Translation:    {express_result[i]["Free Translation"]}')

    translate_result = "\n".join([express_result[i]["Free Translation"].replace('\n', ' ').strip() for i in express_result])

    if len(lines.split('\n')) != len(translate_result.split('\n')):
        print(f'❌ Translation of block {index} failed, Length Mismatch, Please check `output/gpt_log/translate_expressiveness.json`')
        raise ValueError(f'Original ···{lines}···,\nbut got ···{translate_result}···')
    else:
        print(f'✅ Translation of block {index} completed')

    return translate_result, lines


if __name__ == '__main__':
    # test e.g.
    lines = '''All of you know Andrew Ng as a famous computer science professor at Stanford.
He was really early on in the development of neural networks with GPUs.
Of course, a creator of Coursera and popular courses like deeplearning.ai.
Also the founder and creator and early lead of Google Brain.'''
    previous_content_prompt = None
    after_cotent_prompt = None
    things_to_note_prompt = None
    summary_prompt = None
    translate_lines(lines, previous_content_prompt, after_cotent_prompt, things_to_note_prompt, summary_prompt)