"use client"

import type React from "react"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface StepFourProps {
  formData: {
    phone_number: string
    email: string
  }
  updateFormData: (data: any) => void
  errors: any
  visibleFieldIndex: number
}

export default function StepFour({ formData, updateFormData, errors, visibleFieldIndex }: StepFourProps) {
  const handlePhoneNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let value = e.target.value
    // Remove non-digit characters except +
    value = value.replace(/[^+\d]/g, "")
    // Ensure it starts with +233
    if (!value.startsWith("+233")) {
      value = "+233" + value.replace(/^\+233/, "")
    }
    // Limit to +233 and 9 digits
    if (value.length > 13) {
      value = value.slice(0, 13)
    }
    updateFormData({ phone_number: value })
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    updateFormData({ email: e.target.value })
  }

  const fields = [
    {
      id: "phone_number",
      label: "Phone Number (WhatsApp)",
      value: formData.phone_number,
      placeholder: "+233123456789",
      helper: "Enter a valid Ghanaian phone number starting with +233 for WhatsApp notifications.",
      error: errors.phone_number,
      onChange: handlePhoneNumberChange,
      type: "tel",
    },
    {
      id: "email",
      label: "Email (Optional)",
      value: formData.email,
      placeholder: "e.g., teacher@example.com",
      helper: "Provide an email address for additional notifications.",
      error: errors.email,
      onChange: handleEmailChange,
      type: "email",
    },
  ]

  return (
    <div className="space-y-6">
      {fields.map((field, index) => (
        <motion.div
          key={field.id}
          className="space-y-2"
          initial={{ opacity: 0, y: 20 }}
          animate={{
            opacity: index + 1 <= visibleFieldIndex ? 1 : 0,
            y: index + 1 <= visibleFieldIndex ? 0 : 20,
          }}
          transition={{
            duration: 0.4,
            delay: index * 0.1,
            ease: "easeOut",
          }}
        >
          <Label htmlFor={field.id} className={`block text-sm font-medium ${field.error ? "text-red-500" : "text-gray-700"}`}>
            {field.label}
          </Label>
          <Input
            id={field.id}
            name={field.id}
            type={field.type}
            value={field.value}
            onChange={field.onChange}
            placeholder={field.placeholder}
            className={`rounded-lg border-gray-300 shadow-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all ${field.error ? "border-red-500 focus:ring-red-500" : ""}`}
            disabled={index + 1 > visibleFieldIndex}
          />
          <p className="text-sm text-muted-foreground mt-1">{field.helper}</p>
          {field.error && <p className="text-sm text-red-500 mt-1">{field.error}</p>}
        </motion.div>
      ))}
    </div>
  )
}