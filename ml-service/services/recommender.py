class Recommender:
    def suggest(self, message: str, category: str, issues: list, changed_files: list) -> str:
        if not message.strip():
            return "Initial commit" if not changed_files else "Update files"
            
        words = message.split()
        first_word = words[0].lower()
        
        # Determine appropriate verb based on category
        verb = first_word.capitalize()
        if verb.endswith('ed'): verb = verb[:-2]
        elif verb.endswith('ing'): verb = verb[:-3]
        
        if category == "BUG_FIX" and verb.lower() not in ['fix', 'resolve', 'patch']:
            verb = "Fix"
        elif category == "FEATURE" and verb.lower() not in ['add', 'implement', 'create']:
            verb = "Add"
        elif category == "DOCUMENTATION" and verb.lower() not in ['document', 'update']:
            verb = "Update"
        elif category == "REFACTORING" and verb.lower() not in ['refactor', 'clean', 'restructure']:
            verb = "Refactor"
        elif category == "TESTING" and verb.lower() not in ['test', 'add']:
            verb = "Test"
            
        # Determine context from files
        context = ""
        if any("Message doesn't specify which component" in issue for issue in issues):
            if changed_files:
                # Try to guess component from first changed file
                path_parts = changed_files[0].split('/')
                if len(path_parts) > 1:
                    context = f" in {path_parts[-2]}"
                else:
                    context = f" in {path_parts[-1]}"
                    
        # Replace vague words
        rest_of_message = " ".join(words[1:]) if len(words) > 1 else ""
        if "stuff" in rest_of_message.lower() or "things" in rest_of_message.lower():
            if context:
                rest_of_message = "implementation details"
            else:
                rest_of_message = "logic"
                
        if rest_of_message:
            suggestion = f"{verb} {rest_of_message}{context}"
        else:
            if context:
                suggestion = f"{verb} changes{context}"
            else:
                suggestion = f"{verb} {category.lower().replace('_', ' ')}"
                
        return suggestion
        
recommender_service = Recommender()
