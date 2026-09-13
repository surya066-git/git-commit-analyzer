import csv
import os

data = [
    ("add user authentication flow", "FEATURE"),
    ("implement login page", "FEATURE"),
    ("add oauth2 support", "FEATURE"),
    ("create user profile dashboard", "FEATURE"),
    ("add support for dark mode", "FEATURE"),
    
    ("fix null pointer in login", "BUG_FIX"),
    ("fix memory leak in image processing", "BUG_FIX"),
    ("resolve crash on startup", "BUG_FIX"),
    ("fix typo in welcome email", "BUG_FIX"),
    ("fix stuff", "BUG_FIX"),
    ("fix", "BUG_FIX"),
    ("resolve issue with missing token", "BUG_FIX"),
    
    ("refactor payment service", "REFACTORING"),
    ("clean up dead code in auth module", "REFACTORING"),
    ("extract validation logic to separate class", "REFACTORING"),
    ("rename variables for clarity", "REFACTORING"),
    ("simplify complex conditional logic", "REFACTORING"),
    
    ("add unit tests for login", "TESTING"),
    ("update integration tests", "TESTING"),
    ("fix failing test case", "TESTING"),
    ("add e2e tests for checkout", "TESTING"),
    ("test coverage for user service", "TESTING"),
    
    ("update README with setup instructions", "DOCUMENTATION"),
    ("add inline comments to complex algorithm", "DOCUMENTATION"),
    ("document API endpoints", "DOCUMENTATION"),
    ("update changelog for v1.2.0", "DOCUMENTATION"),
    ("docs: improve contribution guidelines", "DOCUMENTATION"),
    
    ("update docker configuration", "CONFIGURATION"),
    ("change port binding to 8080", "CONFIGURATION"),
    ("update dependencies in package.json", "CONFIGURATION"),
    ("add prettier config", "CONFIGURATION"),
    ("configure github actions pipeline", "CONFIGURATION"),
    
    ("optimize database query", "PERFORMANCE"),
    ("reduce bundle size by lazy loading", "PERFORMANCE"),
    ("improve rendering speed of list", "PERFORMANCE"),
    ("cache API responses", "PERFORMANCE"),
    
    ("patch security vulnerability in dependency", "SECURITY"),
    ("sanitize user input to prevent XSS", "SECURITY"),
    ("encrypt passwords before storing", "SECURITY"),
    
    ("update", "OTHER"),
    ("changes", "OTHER"),
    ("wip", "OTHER"),
    ("misc", "OTHER"),
    ("stuff", "OTHER"),
]

# Duplicate and augment for more data
expanded_data = []
for i in range(10):
    for msg, category in data:
        expanded_data.append((msg, category))

os.makedirs('dataset', exist_ok=True)
with open('dataset/commits.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["commit_message", "category"])
    writer.writerows(expanded_data)

print(f"Generated dataset with {len(expanded_data)} samples.")
