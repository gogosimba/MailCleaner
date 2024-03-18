from transformers import pipeline, set_seed

def rewrite_with_gpt2(text):
    generator = pipeline('text-generation', model='gpt2')
    set_seed(42)  # You can change the seed for different outputs
    rewritten_text = generator(text, max_length=150, num_return_sequences=1)[0]['generated_text']
    return rewritten_text

# Example usage
original_text = "We are looking for a skilled software engineer to join our team."

rewritten_text = rewrite_with_gpt2(original_text)
print("Original Text:\n", original_text)
print("\nRewritten Text (GPT-2):\n", rewritten_text)
