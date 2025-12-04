# utils/validators.py
import os
from io import BytesIO

class EcommerceValidators:
    @staticmethod
    def validate_file_upload(file_obj, max_size_mb=200, allowed_extensions=None):
        if allowed_extensions is None:
            allowed_extensions = ['.csv','.xlsx','.xls','.json']

        if file_obj is None:
            return {'valid': False, 'message': 'No file uploaded', 'file_type': None}

        size_mb = len(file_obj.getvalue()) / (1024*1024)
        if size_mb > max_size_mb:
            return {'valid': False, 'message': f'File too large: {size_mb:.1f} MB', 'file_type': None}

        fname = getattr(file_obj, 'name', '')
        _, ext = os.path.splitext(fname.lower())
        if ext not in allowed_extensions:
            return {'valid': False, 'message': f'Unsupported extension: {ext}', 'file_type': None}

        ftype = None
        if ext in ['.csv','.txt']:
            ftype = 'csv'
        elif ext in ['.xlsx','.xls']:
            ftype = 'excel'
        elif ext == '.json':
            ftype = 'json'

        return {'valid': True, 'message': 'valid file', 'file_type': ftype, 'size_mb': size_mb, 'extension': ext}