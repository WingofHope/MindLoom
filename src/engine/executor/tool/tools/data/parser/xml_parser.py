# src/engine/executor/tool/tools/parser/xml_parser.py

import xml.etree.ElementTree as ET
from engine.executor.tool.tools.tool_base import ToolBase

class XMLParser(ToolBase):
    @staticmethod
    def metadata():
        return {
            "id": "parser.xml_parser",
            "name": "xml_parser",
            "description": "解析 XML 文档字符串并转换为嵌套字典。",
            "inputs": [
                {"name": "xml_string", "type": "string", "description": "XML 格式的字符串"}
            ],
            "outputs": [
                {"name": "xml_data", "type": "object", "description": "解析后的嵌套字典数据"}
            ]
        }

    @staticmethod
    def run(inputs):
        """
        工具主逻辑：解析 XML 字符串为嵌套字典。
        参数:
            inputs (dict): 包含键 'xml_string' 的输入字典。
        返回:
            dict: 包含键 'xml_data' 的输出字典，值为解析后的 XML 数据。
        """
        # 获取输入参数
        xml_string = inputs.get("xml_string", "").strip()
        if not xml_string:
            raise ValueError("输入的 \"xml_string\" 参数不能为空。")
        
        try:
            # 将 XML 字符串解析为 ElementTree 的根元素
            root = ET.fromstring(xml_string)
            # 递归解析根元素为嵌套字典
            return {"xml_data": XMLParser._element_to_dict(root)}
        except Exception as e:
            raise ValueError(f"XML文本解析出错，Python执行错误：{e}")

    @staticmethod
    def _element_to_dict(element):
        """
        将 XML 元素递归解析为字典。
        包括：标签名、属性、文本内容以及子元素。
        """
        node = {
            "tag": element.tag,
            "attributes": element.attrib,
            "text": element.text.strip() if element.text else "",
            "children": [XMLParser._element_to_dict(child) for child in element]
        }
        return node