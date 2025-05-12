"use client"

import type React from "react"

import { motion } from "framer-motion"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"

interface StepFiveProps {
  formData: {
    custom_instructions: string
  }
  updateFormData: (data: any) => void
}

export default function StepFive({ formData, updateFormData }: StepFiveProps) {
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const { name, value } = e.target
    updateFormData({ [name]: value })
  }

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
    >
      <div className="space-y-2">
        <Label htmlFor="custom_instructions">Custom Instructions (Optional)</Label>
        <Textarea
          id="custom_instructions"
          name="custom_instructions"
          value={formData.custom_instructions}
          onChange={handleChange}
          placeholder="e.g., Include examples relevant to Ghanaian culture."
          className="min-h-[150px]"
        />
        <p className="text-sm text-muted-foreground mt-1">
          Add any specific requirements or notes for your lesson plan.
        </p>
      </div>
    </motion.div>
  )
}
