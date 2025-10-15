'use client';

import React, { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface MissingField {
  field: string;
  label: string;
  type: 'text' | 'textarea' | 'email' | 'phone';
  required: boolean;
  placeholder?: string;
}

interface MissingInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (data: Record<string, string>) => void;
  missingFields: MissingField[];
  title?: string;
  description?: string;
}

export default function MissingInfoModal({
  isOpen,
  onClose,
  onComplete,
  missingFields,
  title = "Complete Your Resume Information",
  description = "We need some additional information to process your resume effectively."
}: MissingInfoModalProps) {
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    missingFields.forEach(field => {
      if (field.required && (!formData[field.field] || formData[field.field].trim() === '')) {
        newErrors[field.field] = `${field.label} is required`;
      }
      
      // Email validation
      if (field.type === 'email' && formData[field.field]) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData[field.field])) {
          newErrors[field.field] = 'Please enter a valid email address';
        }
      }
      
      // Phone validation
      if (field.type === 'phone' && formData[field.field]) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        if (!phoneRegex.test(formData[field.field].replace(/[\s\-\(\)]/g, ''))) {
          newErrors[field.field] = 'Please enter a valid phone number';
        }
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onComplete(formData);
      setFormData({});
      setErrors({});
    }
  };

  const handleClose = () => {
    setFormData({});
    setErrors({});
    onClose();
  };

  const renderInput = (field: MissingField) => {
    const value = formData[field.field] || '';
    const error = errors[field.field];
    
    if (field.type === 'textarea') {
      return (
        <div key={field.field} className="space-y-2">
          <Label htmlFor={field.field} className="text-sm font-medium text-gray-200">
            {field.label} {field.required && <span className="text-red-400">*</span>}
          </Label>
          <Textarea
            id={field.field}
            value={value}
            onChange={(e) => handleInputChange(field.field, e.target.value)}
            placeholder={field.placeholder || `Enter your ${field.label.toLowerCase()}`}
            className={`bg-gray-800/50 border-gray-600 text-white placeholder-gray-400 focus:border-blue-500 focus:ring-blue-500 ${
              error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''
            }`}
            rows={3}
          />
          {error && <p className="text-sm text-red-400">{error}</p>}
        </div>
      );
    }
    
    return (
      <div key={field.field} className="space-y-2">
        <Label htmlFor={field.field} className="text-sm font-medium text-gray-200">
          {field.label} {field.required && <span className="text-red-400">*</span>}
        </Label>
        <input
          id={field.field}
          type={field.type === 'text' ? 'text' : field.type}
          value={value}
          onChange={(e) => handleInputChange(field.field, e.target.value)}
          placeholder={field.placeholder || `Enter your ${field.label.toLowerCase()}`}
          className={`w-full px-3 py-2 bg-gray-800/50 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
            error ? 'border-red-500 focus:border-red-500 focus:ring-red-500' : ''
          }`}
        />
        {error && <p className="text-sm text-red-400">{error}</p>}
      </div>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px] bg-gray-900/95 border-gray-700 text-white">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 bg-clip-text text-transparent">
            {title}
          </DialogTitle>
          <DialogDescription className="text-center text-gray-300">
            {description}
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 max-h-[400px] overflow-y-auto">
          {missingFields.map(renderInput)}
        </div>
        
        <DialogFooter className="flex gap-3">
          <Button
            variant="outline"
            onClick={handleClose}
            className="border-gray-600 text-gray-300 hover:bg-gray-800"
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-medium px-6 py-2 rounded-md transition-all duration-200"
          >
            Complete Resume
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
