import re
from pathlib import Path

f = Path('src/app/index.tsx')
text = f.read_text(encoding='utf-8')

# 1. Add import for API_BASE_URL
import_statement = "import { API_BASE_URL } from '../config/api';\n"
if "import { API_BASE_URL }" not in text:
    text = text.replace("import { Ionicons } from", import_statement + "import { Ionicons } from")

# 2. Replace API_URL declarations
# We have a few instances of this:
# const API_URL = process.env.EXPO_PUBLIC_API_URL || (Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://127.0.0.1:8000');
old_api_decl = "const API_URL = process.env.EXPO_PUBLIC_API_URL || (Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://127.0.0.1:8000');"
text = text.replace(old_api_decl, "const API_URL = API_BASE_URL;")

# 3. Replace the catch block in submitQuestion
old_catch = '''    } catch (error) {
      console.error("Chat error:", error);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          text: "Sorry, I couldn't reach the backend server. Please try again.",
        },
      ]);
    } finally {'''

new_catch = '''    } catch (error: any) {
      console.error("Chat error:", {
        message: error.message,
        name: error.name,
        url: `${API_URL}/chat`,
        method: "POST"
      });
      
      let errorMessage = "An unexpected error occurred.";
      
      if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
        // Network-level failure (CORS, backend down, wrong URL)
        errorMessage = "Can't reach the assistant right now - check your connection and try again.";
      } else if (error.message && error.message.startsWith("API error:")) {
        // HTTP error (got a response, but it was 4xx/5xx)
        errorMessage = "The server encountered an error processing your request. Please try again.";
      } else if (error instanceof SyntaxError) {
        // JSON parsing failure
        errorMessage = "Received an invalid response from the server. Please try again.";
      } else {
        errorMessage = "Something went wrong: " + error.message;
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          text: errorMessage,
        },
      ]);
    } finally {'''

text = text.replace(old_catch, new_catch)
f.write_text(text, encoding='utf-8')
