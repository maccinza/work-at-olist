import os
from enum import Enum
from io import StringIO
from typing import IO, Set, Union

from django.core.management.base import BaseCommand

from authors.utils import import_authors, import_authors_faster


class MessageType(Enum):
    SUCCESS = "success"
    ERROR = "error"


class Command(BaseCommand):
    help = "Imports authors names from a given csv file into the database"

    def add_arguments(self, parser):
        parser.add_argument("filepath", type=str)
        parser.add_argument("--faster", action="store_true")

    def _write_message(
        self, message: str, message_type: MessageType = MessageType.SUCCESS,
    ) -> None:
        if message_type == MessageType.SUCCESS:
            self.stdout.write(self.style.SUCCESS(message))
        elif message_type == MessageType.ERROR:
            self.stdout.write(self.style.ERROR(message))

    def _collect_data(
        self, filepath: str, faster: bool = False,
    ) -> Union[IO, Set]:
        data = set()
        try:
            with open(filepath, "r", encoding="utf-8") as csv_file:
                next(csv_file, None)
                for line in csv_file:
                    data.add(line.rstrip())
                if faster:
                    content = "\n".join(data)
                    data = StringIO(content)
        except Exception as exc:
            self._write_message(
                f"Error trying to read {filepath}. Got {str(exc)}",
                MessageType.ERROR,
            )
        return data

    def _perform_insertion(
        self, data: Union[IO, Set], filepath: str, faster: bool = False
    ) -> None:
        error_msg = f"Error trying to import authors names from {filepath}. "
        success_message = f"Successfully imported authors from {filepath}"

        if faster:
            try:
                import_authors_faster(data)
            except Exception as exc:
                self._write_message(
                    f"{error_msg} Got {str(exc)}", MessageType.ERROR
                )
            else:
                self._write_message(success_message, MessageType.SUCCESS)
        else:
            try:
                import_authors(data)
            except Exception as exc:
                self._write_message(
                    f"{error_msg} Got {str(exc)}", MessageType.ERROR
                )
            else:
                self._write_message(success_message, MessageType.SUCCESS)

    def handle(self, *args, **options):
        filepath = options.get("filepath", "")
        faster = options.get("faster")

        path_exists = os.path.exists(filepath)
        is_file = os.path.isfile(filepath)
        is_csv = filepath.endswith(".csv")

        if path_exists and is_file and is_csv:
            data = self._collect_data(filepath, faster)

            if data:
                self._perform_insertion(data, filepath, faster)
            else:
                self._write_message(
                    f"Could not collect data from {filepath} properly or the "
                    f"file is empty",
                    MessageType.ERROR,
                )
        else:
            self._write_message(
                f"Provided filepath {filepath} does not exist or is not a file",
                MessageType.ERROR,
            )
