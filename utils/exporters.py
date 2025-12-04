# utils/exporters.py
import pandas as pd
import os
from pathlib import Path
from datetime import datetime

class EcommerceExporters:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_dataframe(self, df: pd.DataFrame, filename: str, format='excel', include_index=False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base = self.output_dir / f"{filename}_{timestamp}"
        try:
            if format == 'excel':
                path = base.with_suffix('.xlsx')
                with pd.ExcelWriter(path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=include_index, sheet_name='data')
                return {'success': True, 'file_path': str(path), 'file_name': path.name}
            elif format == 'csv':
                path = base.with_suffix('.csv')
                df.to_csv(path, index=include_index)
                return {'success': True, 'file_path': str(path), 'file_name': path.name}
            else:
                return {'success': False, 'message': 'unsupported format'}
        except Exception as e:
            return {'success': False, 'message': str(e)}