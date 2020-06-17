import os
import sys
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from authors.management.commands.import_authors import Command, MessageType
from authors.models import Author

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES_DIR = os.path.join(APP_DIR, "tests/fixtures")
EXPECTED_NAMES = {"Richard Flowers", "Jody Vargas", "Susan Myers"}


class TestImportAuthorsCommand(TestCase):
    def test_write_message(self):
        """Command messages are correctly written to stdout"""
        output = StringIO()
        command = Command()
        success_message = f"This is a {MessageType.SUCCESS.value} test message"
        error_message = f"This is an {MessageType.ERROR.value} test message"
        
        with patch.object(command, "stdout", new=output):
            command._write_message(success_message, MessageType.SUCCESS)
            command._write_message(error_message, MessageType.ERROR)
        
        self.assertIn(success_message, output.getvalue())
        self.assertIn(error_message, output.getvalue())

    def test_successful_collect_data(self):
        """It is able to read the input file data into set"""
        command = Command()
        data = command._collect_data(os.path.join(FIXTURES_DIR, "test_authors.csv"))
        self.assertIsInstance(data, set)
        self.assertEqual(data, EXPECTED_NAMES)

    def test_successful_collect_data_faster(self):
        """
        It is able to read the input file data into StringIO with faster parameter
        """
        command = Command()
        data = command._collect_data(
            os.path.join(FIXTURES_DIR, "test_authors.csv"), faster=True
        )
        self.assertIsInstance(data, StringIO)
        self.assertEqual(data.read(), "\n".join(EXPECTED_NAMES))

    def test_failing_collect_data(self):
        """It properly writes to stdout when failing to collect data from file"""
        output = StringIO()
        command = Command()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        error_message = "Simulated error message"
        expected_message = f"Error trying to read {filepath}. Got {error_message}"
        with patch.object(command, "stdout", new=output):
            with patch("builtins.open", side_effect=IOError(error_message)):
                command._collect_data(filepath)
        
        self.assertIn(expected_message, output.getvalue())


    def test_successful_perform_insertion(self):
        """It properly inserts provided authors data into the database"""
        output = StringIO()
        command = Command()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        data = command._collect_data(filepath)

        self.assertEqual(Author.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            command._perform_insertion(data, filepath)

        self.assertIn(
            f"Successfully imported authors from {filepath}",
            output.getvalue()
        )
        self.assertEqual(Author.objects.count(), len(data))

        authors = Author.objects.all()
        for author in authors:
            self.assertIn(author.name, data)

    def test_successful_perform_insertion_duplicated(self):
        """It properly skips inserts of duplicated authors data"""
        output = StringIO()
        command = Command()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        data = command._collect_data(filepath)

        self.assertEqual(Author.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            command._perform_insertion(data, filepath)
            command._perform_insertion(data, filepath)

        self.assertIn(
            f"Successfully imported authors from {filepath}",
            output.getvalue()
        )
        self.assertEqual(Author.objects.count(), len(data))

    def test_failing_perform_insertion(self):
        """It properly writes to stdout when failing to import authors data"""
        output = StringIO()
        command = Command()
        error_message = "Simulated error message"

        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        data = command._collect_data(filepath)

        self.assertEqual(Author.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            with patch(
                "authors.management.commands.import_authors.import_authors",
                side_effect=IOError(error_message)
            ):
                command._perform_insertion(data, filepath)

        self.assertIn(
            f"Error trying to import authors names from {filepath}",
            output.getvalue()
        )
        self.assertIn(error_message, output.getvalue())
        self.assertEqual(Author.objects.count(), 0)

    def test_successful_perform_insertion_faster(self):
        """
        It properly inserts provided authors data into the database
        when 'faster' parameter is provided
        """
        output = StringIO()
        command = Command()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        data = command._collect_data(filepath, faster=True)

        self.assertEqual(Author.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            command._perform_insertion(data, filepath, faster=True)

        self.assertIn(
            f"Successfully imported authors from {filepath}",
            output.getvalue()
        )
        data.seek(0)
        data = {name for name in data.read().split("\n")}
        self.assertEqual(Author.objects.count(), len(data))

        authors = Author.objects.all()
        for author in authors:
            self.assertIn(author.name, data)

    def test_failing_perform_insertion_faster(self):
        """
        It properly writes to stdout when failing to insert authors
        when 'faster' parameter is provided
        """
        output = StringIO()
        command = Command()
        error_message = "Simulated error message"

        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        data = command._collect_data(filepath, faster=True)

        self.assertEqual(Author.objects.count(), 0)
        with patch.object(command, "stdout", new=output):
            with patch(
                "authors.management.commands.import_authors.import_authors_faster",
                side_effect=IOError(error_message)
            ):
                command._perform_insertion(data, filepath, faster=True)

        self.assertIn(
            f"Error trying to import authors names from {filepath}",
            output.getvalue()
        )
        self.assertIn(error_message, output.getvalue())
        self.assertEqual(Author.objects.count(), 0)

    def test_successful_command(self):
        """It successfully inserts the authors when running the command"""
        output = StringIO()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        self.assertEqual(Author.objects.count(), 0)

        call_command("import_authors", filepath, stdout=output)

        self.assertEqual(Author.objects.count(), 3)
        self.assertIn(
            f"Successfully imported authors from {filepath}",
            output.getvalue()
        )

    def test_successful_command_faster(self):
        """
        It successfully inserts the authors when running the command with
        faster parameter
        """
        output = StringIO()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        self.assertEqual(Author.objects.count(), 0)

        call_command("import_authors", filepath, "--faster", stdout=output)

        self.assertEqual(Author.objects.count(), 3)
        self.assertIn(
            f"Successfully imported authors from {filepath}",
            output.getvalue()
        )

    def test_failing_command_data(self):
        """
        It properly writes to stdout when failing to collect the data
        when running the command
        """
        output = StringIO()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        self.assertEqual(Author.objects.count(), 0)

        with patch(
            "authors.management.commands.import_authors.Command._collect_data",
            return_value=None
        ):
            call_command("import_authors", filepath, stdout=output)

        self.assertEqual(Author.objects.count(), 0)
        self.assertIn(
            f"Could not collect data from {filepath} properly or the "
            f"file is empty",
            output.getvalue()
        )

    def test_failing_command_file(self):
        """
        It properly writes to stdout when failing to access the data file
        when running the command
        """
        output = StringIO()
        filepath = os.path.join(FIXTURES_DIR, "test_authors.csv")
        self.assertEqual(Author.objects.count(), 0)

        with patch("os.path.exists", return_value=False):
            call_command("import_authors", filepath, stdout=output)

        self.assertEqual(Author.objects.count(), 0)
        self.assertIn(
            f"Provided filepath {filepath} does not exist or is not a file",
            output.getvalue()
        )
