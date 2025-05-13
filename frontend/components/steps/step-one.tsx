"use client"

import type React from "react"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface StepOneProps {
  formData: {
    subject: string
    class_level: string
    topic: string
  }
  updateFormData: (data: any) => void
  errors: any
  visibleFieldIndex: number
}

export default function StepOne({ formData, updateFormData, errors, visibleFieldIndex }: StepOneProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    updateFormData({ [name]: value })
  }

  const fields = [
    {
      id: "subject",
      label: "Subject",
      value: formData.subject,
      placeholder: "e.g., Mathematics",
      helper: "Enter the subject of the lesson.",
      error: errors.subject,
    },
    {
      id: "class_level",
      label: "Class Level",
      value: formData.class_level,
      placeholder: "e.g., Basic Eight",
      helper: "Specify the class level (e.g., JHS, SHS).",
      error: errors.class_level,
    },
    {
      id: "topic",
      label: "Topic",
      value: formData.topic,
      placeholder: "e.g., Angles and Polygons",
      helper: "Provide the specific topic for the lesson.",
      error: errors.topic,
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
            value={field.value}
            onChange={handleChange}
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