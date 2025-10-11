from typing import List

from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt



class OCRService:
    """
    Service for performing OCR (Optical Character Recognition) tasks.
    
    This class encapsulates the functionality for selecting an image, extracting text
    from the image using the Clarifai API, and identifying UPC codes within the extracted text.
    """
    
    def __init__(self, app_id: str = "app_id", app_secret: str = "app_secret"):
        """
        Initializes the OCRService with Clarifai API credentials.
        
        Args:
            app_id (str, optional): The Clarifai application ID. Defaults to a placeholder "app_id".
            app_secret (str, optional): The Clarifai application secret. Defaults to a placeholder "app_secret".
        """

        self.app_id = app_id
        self.app_secret = app_secret


    def select_image(self, parent) -> str:
        """
        Opens a file dialog for the user to select an image.
        
        Args:
            parent: The parent widget for the file dialog.
        
        Returns:
            str: The path to the selected image file, or an empty string if no file was selected.
        """
        file_dialog = QFileDialog(parent)
        file_dialog.setWindowTitle("Select Image for OCR")
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.jpeg)")
        if file_dialog.exec() == QFileDialog.Accepted:
            return file_dialog.selectedFiles()[0]
        return ""

    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extracts text from the image at the given path using the Clarifai API.
        
        Args:
            image_path (str): The path to the image file.
        
        Returns:
            str: The extracted text from the image, or an empty string if extraction fails.
        """
        try:
            # Placeholder implementation: Return image path if no API keys are entered.
            if self.app_id == "app_id" or self.app_secret == "app_secret":
                QMessageBox.information(None, "Clarifai API", "No API Keys are configured, Using OCR on file name.")
                return image_path

            # In a real implementation, you would use the Clarifai API here
            # to extract text from the image. The extracted text would then be
            # returned.

            # Replace this placeholder with actual Clarifai API code.
            from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
            channel = ClarifaiChannel.get_grpc_channel()
            stub = service_pb2_grpc.V2Stub(channel)
            metadata = (("authorization", "Key " + self.app_secret),)
            
            request = resources_pb2.MultiInput(
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            image=resources_pb2.Image(
                                url=f"file://{image_path}" #Loads from disk
                            )
                        )
                    )
                ]
            )
            
            response = stub.PostModelOutputs(
                service_pb2.PostModelOutputsRequest(
                    model_id="invoice-parser",
                    inputs=request
                ),
                metadata=metadata
            )
            
            if response.status.code != status_code_pb2.SUCCESS:
                raise Exception(f"Request failed with status code {response.status.code}")
            
            data = response.outputs[0].data.text.raw
            
            if not data:
                return image_path
            
            return data  # Placeholder
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""

    def find_upc_codes(self, text: str) -> List[str]:
        """
        Identifies UPC codes within the given text.
        
        Args:
            text (str): The text to search for UPC codes.
        
        Returns:
            List[str]: A list of UPC codes found in the text.
        """
        import re

        try:
            # This regex is a simplified version and might need adjustments
            # for more complex UPC code formats.
            upc_pattern = re.compile(r'\b(\d{12})\b')
            upc_codes = upc_pattern.findall(text)
            return upc_codes
        except Exception as e:
            print(f"Error finding UPC codes in text: {e}")
            return []
    
    def perform_image_ocr(self, parent) -> None:
        """
        Opens a file dialog for the user to select an image, extracts text from the image using the Clarifai API, and identifies UPC codes within the extracted text.
        Displays a message box with the results.
        
        Args:
            parent: The parent widget for the file dialog.
        """

        try:
            # Select image
            image_path = self.select_image(parent)
            if not image_path:
                QMessageBox.information(parent, "OCR Canceled", "OCR operation cancelled.")
                return
            
            # Extract text from image
            extracted_text = self.extract_text_from_image(image_path)
            if extracted_text == image_path:
                QMessageBox.warning(parent, "OCR Failed", "Could not extract text from the image.")
                return
            
            # Find UPC codes
            upc_codes = self.find_upc_codes(extracted_text)
            
            # Display results
            if upc_codes:
                message = f"Found UPC codes: {', '.join(upc_codes)}"
                QMessageBox.information(parent, "OCR Result", message)
            else:
                QMessageBox.warning(parent, "OCR Result", "No UPC codes found in the image.")
        
        except Exception as e:
            QMessageBox.critical(parent, "OCR Error", f"OCR process failed: {str(e)}")

    def get_image_from_path(self, image_path):
        """Load Image from Path"""
        try:
            image = QImage(image_path)
            if image.isNull():
                raise ValueError(f"Invalid image file: {image_path}")
            return QPixmap.fromImage(image)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None