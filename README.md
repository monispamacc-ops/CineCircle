# <center> 🎬 CineCircle Movie Hub </center>

***

## **🏗️ System Architecture**
CineCircle is built as a data-driven web application designed for simplicity, interactivity, and seamless database synchronization.

*   **Frontend Interface:** Streamlit (Python) for an intuitive, interactive dashboard.
*   **Database:** Aiven MySQL Cloud instance for persistent, remote data storage.
*   **Connectivity:** Python `mysql-connector` for secure, low-latency database interaction.
*   **Deployment:** Hosted via Streamlit Cloud with integrated GitHub CI/CD pipeline.

## **🚀 Key Features**
1.  **Shared Watchlist:** Add movies to a centralized pool viewable by all registered friends.
2.  **Community Ratings:** Submit, update, or delete star ratings for any movie in the list.
3.  **Review System:** Write short reviews and read feedback from others in a dedicated, clean interface.
4.  **Data Safety:** Built-in safeguards for destructive actions, preventing accidental data loss with clear UI cues.

## **🛠️ Engineering Implementations**
*   **Relational Database Modeling:** Designed a two-table schema (`movies` and `ratings`) with Foreign Key constraints to ensure data integrity between movie entries and user feedback.
*   **Dynamic ID Mapping:** Implemented helper functions to bridge the gap between user-friendly movie titles (frontend) and numeric database IDs (backend), ensuring smooth CRUD operations.
*   **Asynchronous UX:** Utilized Streamlit’s rerendering capabilities to provide immediate visual feedback upon submitting or deleting reviews.

## **📁 Project Structure**
```text
CineCircle/
├── streamapp.py      # Main UI and dashboard logic
├── db_manager.py     # Database connection and query handlers
├── requirements.txt  # Project dependencies
└── README.md         # Project documentation
