# A Small Tool for Downloading Dune CSVs 📊

This is a little Streamlit web app I put together to help fetch results from a Dune Analytics query and download them as a CSV file. I hope you find it useful.

---

## ✨ A Few Features

* **A straightforward interface**: I tried to make the UI clean and simple for entering a Dune API key and a Query ID.
* **Password-style input for security**: The API key input is treated like a password, so it stays hidden on the screen.
* **Some basic error handling**: The app tries to provide feedback for common issues like an invalid API key or a wrong Query ID.
* **Data preview**: It shows a small preview of the fetched data right in the app.
* **CSV Download**: Lets you download the full query results as a UTF-8 encoded CSV file.
* **Remembers your inputs**: It uses Streamlit's session state to hold onto your inputs during a session.

---

## 🚀 How to Use It

1. **Enter API Key**: You can paste your Dune API key into the first input box. This can be found on your [Dune Analytics user settings page](https://dune.com/settings).
2. **Enter Query ID**: Next, you can put in the numerical ID of the Dune query you'd like to fetch. This ID is in the URL of the query page (e.g., `https://dune.com/queries/2833363`).
3. **Get Results**: Clicking the `🚀 Get Query Results` button will start the process. A loading spinner will appear while the data is being fetched.
4. **Preview & Download**:
   * If everything works, a preview of the data should appear.
   * The `📥 Download Results as CSV` button will then show up, which you can click to save the file.

---

## 💻 Running it Locally

If you'd like to run this on your own machine, here are the steps.

### Prerequisites

* Python 3.8+
* pip (Python package installer)

### 1. Get the Code

You'll need to clone or download the project files to your computer.

### 2. Create a `requirements.txt` file

This file helps manage the project's dependencies. Just create a file named `requirements.txt` and add these lines:

```
streamlit
pandas
requests
```

### 3. Install the Packages

Open your terminal, go to the project's directory, and run this command:

```bash
pip install -r requirements.txt
```

### 4. Run the App

After the packages are installed, you can start the app with this command:

```bash
streamlit run your_script_name.py
```

Just be sure to replace `your_script_name.py` with the name of the Python file. The app should then open in a new browser tab.

---
Hope this little tool is helpful! Any feedback is welcome.
