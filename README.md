# AI Public Speaking Assistant - Flask & Gemini

## Overview

This project implements a Flask web application that serves as an AI-powered assistant for public speaking preparation, practice, and analysis. It leverages Google's Gemini (specifically `gemini-1.5-flash`) to provide context-aware responses to user queries, focusing on providing useful suggestions and tools within the domain of public speaking. The application manages chat history, handles out-of-scope requests gracefully, and uses markdown formatting for better readability.

## Features

*   **AI-Powered Chat:** Uses Google Gemini to generate conversational responses to user input.
*   **Public Speaking Focus:**  Provides assistance with brainstorming, outlining, writing content, suggesting improvements, and discussing AI tools for public speaking.
*   **Context-Aware Responses:**  Maintains chat history to provide relevant responses.  Handles follow-up commands and clarification questions intelligently.
*   **Out-of-Scope Handling:**  Gracefully declines requests that fall outside the defined scope with a specific message.
*   **Markdown Formatting:**  Uses Markdown for clear and readable output.
*   **Error Handling:** Includes robust error handling and logging.
*   **User-Friendly Interface:**  A simple HTML interface (provided in `templates/index.html`) to interact with the chatbot.

## Technologies

*   **Python:** The primary programming language.
*   **Flask:** A micro web framework for building the web application.
*   **Google Generative AI (genai):**  Used to interact with Google Gemini models.
*   **dotenv:**  Used to load environment variables from a `.env` file.
*   **HTML, CSS, JavaScript:** For the user interface (basic implementation provided).

## Prerequisites

*   **Python 3.7+:**  Ensure you have Python installed.
*   **Google API Key:** You need a valid Google API key for the Gemini API. Get this from the Google AI Studio.
*   **Pip:** Python's package installer.

## Installation

1.  **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_name>
    ```

2.  **Create a Virtual Environment (recommended):**

    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # On Windows
    source .venv/bin/activate # On macOS/Linux
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    (If you don't have a `requirements.txt`, create one with the following content:)
    ```
    Flask
    python-dotenv
    google-generativeai
    ```

4.  **Configure Environment Variables:**

    *   Create a `.env` file in the project root.
    *   Add your Google API key:

        ```
        GOOGLE_API_KEY=YOUR_GOOGLE_API_KEY
        FLASK_SECRET_KEY=YOUR_SECRET_KEY  # Replace with a strong secret key for production
        ```

    *   Replace `YOUR_GOOGLE_API_KEY` and `YOUR_SECRET_KEY` with your actual values.  **Crucially, set a strong, random secret key in production.**

## Running the Application

1.  **Run the Flask app:**

    ```bash
    python app.py
    ```

2.  **Access the application:**  Open your web browser and go to `http://127.0.0.1:5000/` (or the address displayed in your terminal).

## Usage

1.  **Start a Conversation:**  Enter your message in the text box and submit it.
2.  **Ask about Public Speaking:**  Ask questions or make requests related to speech preparation, practice, or analysis.
3.  **Follow-up:** The chatbot will maintain context.  Use follow-up commands and clarification to develop ideas.
4.  **Out-of-Scope Detection:** If you ask a question outside of the defined scope, the bot will respond with an out-of-scope message.

## Code Structure

*   `app.py`: Contains the Flask application, routes, chatbot logic, and Gemini API interaction.
*   `templates/index.html`:  The HTML template for the web interface. (Basic implementation).
*   `.env`: Stores environment variables (API keys, etc.).
*   `requirements.txt`: Lists the Python package dependencies.

## Key Files

*   `app.py`:  The core logic of the application.  Contains the Flask app setup,  API interaction, and the `generate_response_gemini` function (the key part for Gemini interaction and prompt/scope handling).
*   `templates/index.html`:  Provides the user interface.
*   `.env`:  Used for storing the API key and secret key

## Scope and Limitations

*   **Scope:** The application is designed to focus solely on AI tools and techniques for public speaking preparation, practice, and analysis.
*   **Limitations:**
    *   The response quality depends on the Gemini model and prompt engineering.
    *   The application's functionality is limited to the defined scope.
    *   Error handling may need improvement.
    *   The UI is basic.

## Future Improvements

*   **Enhanced UI:** Improve the user interface with more features and better styling.
*   **Improved Prompt Engineering:** Refine prompts for better responses and context understanding.
*   **More Robust Error Handling:**  Implement more comprehensive error handling and logging.
*   **Additional Gemini Models:**  Experiment with different Gemini models.
*   **User Authentication:** Add user authentication to manage sessions securely.
*   **More AI Tools Integration:** Integrate with other AI tools for speech analysis and feedback.

## Contributing

Contributions are welcome!  Feel free to submit pull requests or open issues to suggest improvements or report bugs.

## Permission

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

## Conditions

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

## Disclaimer

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
