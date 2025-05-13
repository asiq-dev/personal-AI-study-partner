# Personal AI Study Partner

This project is a Django-based application designed to serve as a personal AI-powered study partner. It aims to assist users in learning and improving their knowledge through interactive and intelligent features.

## Features

- **AI-Powered Assistance**: Leverages AI to provide personalized study recommendations and answers.
- **User-Friendly Interface**: Simple and intuitive design for seamless interaction.
- **Progress Tracking**: Tracks user progress and provides insights for improvement.
- **Customizable Topics**: Allows users to focus on specific areas of interest.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/personal-AI-study-partner.git
    ```
2. Navigate to the project directory:
    ```bash
    cd personal-AI-study-partner
    ```
3. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5. Apply migrations:
    ```bash
    python manage.py migrate

6. Google Sheets Integration (Required Setup):
    ```bash
    To enable integration with Google Sheets (e.g., for logging study sessions, syncing content, or storing user progress), you need to manually add a `credentials` folder with Google API credentials.
    - mkdir credentials
    # move the credentials.json here
    Your structure should look like:
    personal-AI-study-partner/
    ├── credentials/
    │   └── credentials.json

    ```
7. Run the development server:
    ```bash
    python manage.py runserver
    ```

## Usage

1. Open your browser and navigate to `http://127.0.0.1:8000/`.
2. Register or log in to start using the application.
3. Explore the features and customize your study preferences.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Thanks to the Django community for their excellent framework.
- Special thanks to contributors and testers for their support.
