
class ConfirmationManager:
    def __init__(self):
        self.pending_confirmation = None
        self.highlighted_element = None
    def set_pending(self, element, text, original_query):
        self.pending_confirmation = {
            'element': element,
            'text': text,
            'original_query': original_query
        }
        self.highlighted_element = element
    def has_pending(self):
        return self.pending_confirmation is not None
    def get_pending(self):
        return self.pending_confirmation
    def clear(self):
        self.pending_confirmation = None
        self.highlighted_element = None
    def confirm(self):
        if self.pending_confirmation:
            element = self.pending_confirmation['element']
            self.clear()
            return element
        return None
    def reject(self):
        self.clear()
        return False