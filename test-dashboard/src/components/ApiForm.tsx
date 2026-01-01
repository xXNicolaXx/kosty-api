import React from 'react';
import './ApiForm.css';

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select' | 'number';
  placeholder?: string;
  options?: string[];
  defaultValue?: string | number;
  required?: boolean;
  isArray?: boolean;
  help?: string;
}

interface ApiFormProps {
  fields: FormField[];
  onSubmit: (data: Record<string, any>) => void;
  loading: boolean;
}

const ApiForm: React.FC<ApiFormProps> = ({ fields, onSubmit, loading }) => {
  const [formData, setFormData] = React.useState<Record<string, any>>(() => {
    const initial: Record<string, any> = {};
    fields.forEach(field => {
      if (field.defaultValue !== undefined) {
        initial[field.name] = field.defaultValue;
      }
    });
    return initial;
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Process form data
    const processedData: Record<string, any> = {};
    
    Object.entries(formData).forEach(([key, value]) => {
      const field = fields.find(f => f.name === key);
      
      if (field?.isArray && typeof value === 'string') {
        // Convert comma-separated string to array
        processedData[key] = value.split(',').map(v => v.trim()).filter(v => v);
      } else if (value !== '' && value !== null && value !== undefined) {
        processedData[key] = value;
      }
    });
    
    onSubmit(processedData);
  };

  const handleChange = (name: string, value: any) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <form className="api-form" onSubmit={handleSubmit}>
      {fields.map(field => (
        <div key={field.name} className="form-field">
          <label htmlFor={field.name}>
            {field.label}
            {field.required && <span className="required">*</span>}
          </label>
          
          {field.type === 'textarea' ? (
            <textarea
              id={field.name}
              name={field.name}
              placeholder={field.placeholder}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              required={field.required}
              rows={3}
            />
          ) : field.type === 'select' ? (
            <select
              id={field.name}
              name={field.name}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              required={field.required}
            >
              <option value="">Select...</option>
              {field.options?.map(option => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          ) : (
            <input
              id={field.name}
              name={field.name}
              type={field.type}
              placeholder={field.placeholder}
              value={formData[field.name] || ''}
              onChange={(e) => handleChange(field.name, e.target.value)}
              required={field.required}
            />
          )}
          
          {field.help && <small className="help-text">{field.help}</small>}
        </div>
      ))}
      
      <button type="submit" disabled={loading} className="submit-button">
        {loading ? 'Loading...' : 'Test API'}
      </button>
    </form>
  );
};

export default ApiForm;
