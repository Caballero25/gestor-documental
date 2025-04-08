
from django.views.generic import DetailView
from .models import Document
import base64

class DocumentView(DetailView):
    model = Document
    template_name = 'gestor/document_view.html'
    context_object_name = 'document'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ver Documento'
        context['breadcrumb_previous'] = "Documentos"
        context['breadcrumb_previous_link'] = "document_list"
        document = self.object
        
        # Leer el archivo y convertirlo a base64
        if document.file:
            try:
                with document.file.open('rb') as file:
                    file_content = file.read()
                    file_base64 = base64.b64encode(file_content).decode('utf-8')

                    context['file_base64'] = file_base64
                    
                    # Incluir tipo MIME si es necesario
                    import mimetypes
                    mime_type, _ = mimetypes.guess_type(document.file.name)
                    context['mime_type'] = mime_type
            except Exception as e:
                context['file_error'] = str(e)
        
        return context