import fitz


class PDFProcessor:

    @staticmethod
    def extract_text(pdf_path):

        document = fitz.open(pdf_path)

        pages = []

        for page_number in range(len(document)):
            page = document.load_page(page_number)

            pages.append(
                {
                    "page_number": page_number + 1,
                    "text": page.get_text()
                }
            )

        document.close()

        return pages