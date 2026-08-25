import csv
import logging
import os
import threading
from typing import List, Dict


logger = logging.getLogger(__name__)

HISTORY_FILE = "chat_history.csv"

# Basic lock so simultaneous requests don't write to the CSV at the same time.
_history_lock = threading.Lock()


def initialize_history():
    """
    Create the history CSV when the application starts.
    """
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["query", "response"],
            )
            writer.writeheader()

        logger.info("Created chat history file: %s", HISTORY_FILE)


def get_last_history(limit: int = 5) -> List[Dict[str, str]]:
    """
    Return the last `limit` query/response pairs.
    """

    if not os.path.exists(HISTORY_FILE):
        return []

    with _history_lock:
        with open(HISTORY_FILE, "r", newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

    history = rows[-limit:]

    logger.info("Selected %d previous queries for history", len(history))

    for index, item in enumerate(history, start=1):
        logger.info(
            "History query %d: %s",
            index,
            item["query"],
        )

    return history


def save_history(query: str, response: str):
    """
    Append the current query/response to the CSV.
    """

    with _history_lock:
        with open(
            HISTORY_FILE,
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=["query", "response"],
            )

            writer.writerow(
                {
                    "query": query,
                    "response": response,
                }
            )

    logger.info("Saved query to history: %s", query)
