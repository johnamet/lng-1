"use client"

import type React from "react"
import { motion } from "framer-motion"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface StepTwoProps {
  formData: {
    week_ending: string
    duration: string
    days: string
    week: string
  }
  updateFormData: (data: any) => void
  errors: any
  visibleFieldIndex: number
}

export default function StepTwo({ formData, updateFormData, errors, visibleFieldIndex }: StepTwoProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    updateFormData({ [name]: value })
  }

  const fields = [
    {
      id: "week_ending",
      label: "Week Ending",
      value: formData.week_ending,
      placeholder: "e.g., 16th May, 2025",
      helper: "Enter the date the week ends.",
      error: errors.week_ending,
    },
    {
      id: "duration",
      label: "Duration",
      value: formData.duration,
      placeholder: "e.g., 4 periods per class",
      helper: "Specify the duration of the lesson per class.",
      error: errors.duration,
    },
    {
      id: "days",
      label: "Days",
      value: formData.days,
      placeholder: "e.g., Monday - Friday",
      helper: "List the days the lessons will occur.",
      error: errors.days,
    },
    {
      id: "week",
      label: "Week Number",
      value: formData.week,
      placeholder: "e.g., 3",
      helper: "Enter the week number in the term.",
      error: errors.week,
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