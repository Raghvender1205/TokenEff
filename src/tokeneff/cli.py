import argparse
from tokeneff.core.models import ConversionInput
from tokeneff.core.converters.json_converter import JsonConverter
from tokeneff.formatters.toon_formatter import ToonFormatter


def main():
    parser = argparse.ArgumentParser(description="Token Efficient Data Converter")
    parser.add_argument("--input", required=True, help="Input file")
    parser.add_argument(
        "--format", default="json", help="Input format (json, csv, yaml)"
    )
    args = parser.parse_args()

    with open(args.input, "r") as f:
        raw_data = f.read()

    # TODO: Select converter dynamically
    converter = JsonConverter()
    formatter = ToonFormatter()

    normalized = converter.parse(ConversionInput(data=raw_data, format=args.format))
    output = formatter.format(normalized)

    print("Token-efficient output:\n", output.content)
    print(f"\nToken count: {output.token_count}")
