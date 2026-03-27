from typing import Optional
import PyPDF2
from docx import Document
from app.core.config import settings


class FileParser:
    """文件解析器"""
    
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析PDF文件"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Failed to parse PDF: {str(e)}")
        return text
    
    @staticmethod
    def parse_word(file_path: str) -> str:
        """解析Word文件"""
        text = ""
        try:
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Failed to parse Word document: {str(e)}")
        return text
    
    @staticmethod
    def parse_markdown(file_path: str) -> str:
        """解析Markdown文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to parse Markdown: {str(e)}")
    
    @staticmethod
    def parse_text(file_path: str) -> str:
        """解析文本文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to parse text file: {str(e)}")
    
    @classmethod
    def parse_file(cls, file_type: str, file_path: str) -> str:
        """根据文件类型解析文件"""
        parsers = {
            'pdf': cls.parse_pdf,
            'word': cls.parse_word,
            'markdown': cls.parse_markdown,
            'text': cls.parse_text
        }
        
        parser = parsers.get(file_type)
        if not parser:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        return parser(file_path)