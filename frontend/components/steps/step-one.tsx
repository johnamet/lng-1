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
      error: errors.subject,
    },
    {
      id: "class_level",
      label: "Class Level",
      value: formData.class_level,
      placeholder: "e.g., Basic Eight",
      error: errors.class_level,
    },
    {
      id: "topic",
      label: "Topic",
      value: formData.topic,
      placeholder: "e.g., Angles and Polygons",
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
            opacity: index <= visibleFieldIndex ? 1 : 0,
            y: index <= visibleFieldIndex ? 0 : 20,
          }}
          transition={{
            duration: 0.5,
            ease: "easeOut",
          }}
        >
          <Label htmlFor={field.id} className={field.error ? "text-red-500" : ""}>
            {field.label}
          </Label>
          <Input
            id={field.id}
            name={field.id}
            value={field.value}
            onChange={handleChange}
            placeholder={field.placeholder}
            className={field.error ? "border-red-500 focus-visible:ring-red-500" : ""}
            disabled={index > visibleFieldIndex}
          />
          {field.error && <p className="text-sm text-red-500 mt-1">{field.error}</p>}
        </motion.div>
      ))}
    </div>
  )
}
