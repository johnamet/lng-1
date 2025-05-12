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
      error: errors.week_ending,
    },
    {
      id: "duration",
      label: "Duration",
      value: formData.duration,
      placeholder: "e.g., 4 periods per class",
      error: errors.duration,
    },
    {
      id: "days",
      label: "Days",
      value: formData.days,
      placeholder: "e.g., Monday - Friday",
      error: errors.days,
    },
    {
      id: "week",
      label: "Week Number",
      value: formData.week,
      placeholder: "e.g., 3",
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
