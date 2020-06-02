import re
from collections import Counter
from utils.logger import Logger

from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LTTextBoxHorizontal, LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTLine, LTCurve, LTChar, LTAnno
from pdfminer.converter import PDFPageAggregator


class PDFpreprocess:

    def __init__(self):
        pass

    def extract_paragraphs_from_pdf(self, pdf_objects: list) -> None:
        # Create resource manager
        rsrcmgr = PDFResourceManager()
        # Set parameters for analysis.
        laparams = LAParams()
        # Create a PDF page aggregator object.
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        self.paragraphs_dict = {0: {"str": "",
                                    "page": 0}}

        j = 1
        for pageNumber, page in enumerate(pdf_objects):
            pageNumber_shift = pageNumber + 1
            interpreter.process_page(page)
            # receive the LTPage object for the page.
            layout = device.get_result()
            for element in layout:
                if isinstance(element, LTTextBox):  # LTTextBoxHorizontal
                    text = element.get_text()
                    text_splitted = text.split("\n \n")
                    for tmp in text_splitted:
                        if len(tmp) >= 20:
                            tmp = tmp.replace("\n", "")
                            # tmp.replace("•", "-")
                            if tmp[0] == ' ':
                                tmp = tmp[1:]
                            if tmp[-1] == ' ':
                                tmp = tmp[0:-1]
                            if tmp[0].islower():
                                self.paragraphs_dict[j - 1] = {"str": self.paragraphs_dict[j - 1]["str"] + tmp,
                                                               "page": pageNumber_shift}
                            elif ";" in self.paragraphs_dict[j - 1]["str"][-8:] or \
                                    ":" in self.paragraphs_dict[j - 1]["str"][-8:]:
                                self.paragraphs_dict[j - 1] = {"str": self.paragraphs_dict[j - 1]["str"] + tmp,
                                                               "page": pageNumber_shift}
                            else:
                                self.paragraphs_dict[j] = {"str": tmp,
                                                           "page": pageNumber_shift}
                                j += 1
        self.paragraphs_dict.pop(0, None)


    def convert_paragraphs_to_nlp(self, nlp) -> None:
        for i in self.paragraphs_dict.keys():
            doc_nlp = nlp(self.paragraphs_dict[i]["str"])
            try:
                self.paragraphs_dict[i].update({"nlp": [nlp(sent.string.strip()) for sent in doc_nlp.sents]})
                self.paragraphs_dict[i].update({"page": self.paragraphs_dict[i]["page"]})
            except:
                pass
            print("paragraph:" + str(i) + "done")
