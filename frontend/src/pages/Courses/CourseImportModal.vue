<template>
	<Dialog
		v-model="show"
		:options="{
			title: __('Import Course from ZIP'),
		}"
	>
		<template #body-title>
			<div class="bhasha-dialog-heading">
				<div class="bhasha-dialog-icon" aria-hidden="true">
					<FileArchive class="size-5 stroke-1.75" />
				</div>
				<div>
					<h3 class="bhasha-dialog-title">{{ __('Import a course ZIP') }}</h3>
					<p class="bhasha-dialog-description">
						{{
							__(
								'Restore a course exported from Bhasha. The ZIP should include the complete course package.',
							)
						}}
					</p>
				</div>
			</div>
		</template>
		<template #body-content>
			<div class="bhasha-zip-form text-p-base">
				<div
					v-if="!zip"
					@dragover.prevent
					@drop.prevent="(e) => uploadFile(e)"
					class="bhasha-zip-dropzone"
				>
					<div v-if="!uploading" class="w-4/5 text-center">
						<div class="bhasha-upload-icon" aria-hidden="true">
							<UploadCloud class="size-6 stroke-1.5" />
						</div>
						<input
							ref="fileInput"
							type="file"
							class="hidden"
							accept=".zip"
							@change="(e) => uploadFile(e)"
						/>
						<div class="bhasha-upload-title">
							{{ __('Drag and drop your ZIP file here') }}
						</div>
						<div class="bhasha-upload-description">
							{{ __('or') }}
							<button
								type="button"
								@click="openFileSelector"
								class="bhasha-upload-link"
							>
								{{ __('browse files') }}
							</button>
							{{ __('from your device') }}
						</div>
					</div>
					<div
						v-else-if="uploading"
						class="bhasha-upload-progress"
					>
						<div class="space-y-2">
							<div class="font-medium">
								{{ uploadingFile.name }}
							</div>
							<div class="text-ink-gray-6">
								{{ convertToMB(uploaded) }} of {{ convertToMB(total) }}
							</div>
						</div>
						<div class="bhasha-upload-progress-track">
							<div
								class="bhasha-upload-progress-bar"
								:style="`width: ${uploadProgress}%`"
							></div>
						</div>
					</div>
				</div>
				<div
					v-else-if="zip"
					class="bhasha-zip-dropzone is-complete"
				>
					<div
						class="bhasha-uploaded-file"
					>
						<div class="bhasha-uploaded-file-icon" aria-hidden="true">
							<FileArchive class="size-5 stroke-1.5" />
						</div>
						<div class="min-w-0 flex-1 space-y-1">
							<div class="font-medium leading-5 text-ink-gray-9">
								{{ zip.file_name || zip.name }}
							</div>
							<div v-if="zip.file_size" class="text-ink-gray-6">
								{{ convertToMB(zip.file_size) }}
							</div>
						</div>
						<button
							type="button"
							class="bhasha-remove-upload"
							:aria-label="__('Remove ZIP file')"
							@click="deleteFile"
						>
							<Trash2 class="size-4 stroke-1.5" />
						</button>
					</div>
				</div>
			</div>
		</template>
		<template #actions="{ close }">
			<div class="bhasha-dialog-actions">
				<Button
					class="bhasha-dialog-secondary"
					variant="outline"
					size="md"
					@click="close"
				>
					{{ __('Cancel') }}
				</Button>
				<Button
					class="bhasha-primary bhasha-dialog-primary"
					variant="solid"
					size="md"
					:disabled="!zip || uploading"
					@click="importZip"
				>
					{{ __('Import course') }}
				</Button>
			</div>
		</template>
	</Dialog>
</template>
<script setup lang="ts">
import { Button, call, Dialog, FileUploadHandler, toast } from 'frappe-ui'
import { computed, ref } from 'vue'
import { FileArchive, Trash2, UploadCloud } from 'lucide-vue-next'
import { useRouter } from 'vue-router'

const fileInput = ref<HTMLInputElement | null>(null)
const show = defineModel<boolean>({ required: true, default: false })
const zip = ref<any | null>(null)
const uploaded = ref(0)
const total = ref(0)
const uploading = ref(false)
const uploadingFile = ref<any | null>(null)
const router = useRouter()

const openFileSelector = () => {
	fileInput.value?.click()
}

const uploadProgress = computed(() => {
	if (total.value === 0) return 0
	return Math.floor((uploaded.value / total.value) * 100)
})

const extractFile = (e: Event): File | null => {
	const inputFiles = (e.target as HTMLInputElement)?.files
	const dt = (e as DragEvent).dataTransfer?.files

	return inputFiles?.[0] || dt?.[0] || null
}

const validateFile = (file: File) => {
	const extension = file.name.split('.').pop()?.toLowerCase()
	if (extension !== 'zip') {
		toast.error('Please upload a valid ZIP file.')
		console.error('Please upload a valid ZIP file.')
	}
	return extension
}

const uploadFile = (e: Event) => {
	const file = extractFile(e)
	if (!file) return

	let fileType = validateFile(file)
	if (fileType !== 'zip') return

	uploadingFile.value = file
	const uploader = new FileUploadHandler()

	uploader.on('start', () => {
		uploading.value = true
	})

	uploader.on('progress', (data: { uploaded: number; total: number }) => {
		uploaded.value = data.uploaded
		total.value = data.total
	})

	uploader.on('error', (error: any) => {
		uploading.value = false
		toast.error(__('File upload failed. Please try again.'))
		console.error('File upload error:', error)
	})

	uploader.on('finish', () => {
		uploading.value = false
	})
	uploader
		.upload(file, {
			private: 1,
		})
		.then((data: any) => {
			zip.value = data
		})
		.catch((error: any) => {
			console.error('File upload error:', error)
			toast.error(__('File upload failed. Please try again.'))
			uploading.value = false
			uploadingFile.value = null
			uploaded.value = 0
			total.value = 0
		})
}

const importZip = () => {
	if (!zip.value) return
	call('lms.lms.api.import_course_from_zip', {
		zip_file_path: zip.value.file_url,
	})
		.then((data: any) => {
			toast.success('Course imported successfully!')
			show.value = false
			deleteFile()
			router.push({
				name: 'CourseDetail',
				params: { courseName: data },
			})
		})
		.catch((error: any) => {
			toast.error('Error importing course: ' + error.message)
			console.error('Error importing course:', error)
		})
}

const deleteFile = () => {
	zip.value = null
	uploadingFile.value = null
	uploaded.value = 0
	total.value = 0
	if (fileInput.value) fileInput.value.value = ''
}

const convertToMB = (bytes: number) => {
	return (bytes / 1024 / 1024).toFixed(2) + ' MB'
}
</script>

<style>
.bhasha-zip-dropzone {
	display: flex;
	min-height: 12rem;
	align-items: center;
	justify-content: center;
	padding: 1.5rem;
	border: 1.5px dashed rgba(101, 50, 197, 0.32);
	border-radius: 1.25rem;
	background:
		linear-gradient(rgba(246, 242, 255, 0.74), rgba(255, 255, 255, 0.9));
	transition:
		border-color 160ms ease,
		background-color 160ms ease;
}

.bhasha-zip-dropzone:hover {
	border-color: var(--bhasha-500);
	background: var(--bhasha-50);
}

.bhasha-upload-icon {
	display: grid;
	width: 3rem;
	height: 3rem;
	margin: 0 auto 0.875rem;
	place-items: center;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: 0.875rem;
	background: var(--bhasha-surface);
	color: var(--bhasha-700);
	box-shadow: 0 5px 14px rgba(61, 34, 111, 0.08);
}

.bhasha-upload-title {
	color: var(--bhasha-text);
	font-weight: 700;
	line-height: 1.45;
}

.bhasha-upload-description {
	margin-top: 0.35rem;
	color: var(--bhasha-text-muted);
	font-size: 0.8125rem;
	line-height: 1.5;
}

.bhasha-upload-link {
	color: var(--bhasha-700);
	font-weight: 750;
	text-decoration: underline;
	text-decoration-color: var(--bhasha-300);
	text-underline-offset: 0.18rem;
}

.bhasha-upload-link:hover {
	color: var(--bhasha-600);
	text-decoration-color: currentColor;
}

.bhasha-upload-link:focus-visible {
	border-radius: 0.25rem;
	outline: none;
	box-shadow: var(--bhasha-focus-ring);
}

.bhasha-upload-progress,
.bhasha-uploaded-file {
	width: min(100%, 23rem);
	padding: 1rem;
	border: 1px solid var(--bhasha-border-brand);
	border-radius: var(--bhasha-radius-control);
	background: var(--bhasha-surface);
	box-shadow: 0 8px 20px rgba(61, 34, 111, 0.08);
}

.bhasha-upload-progress-track {
	width: 100%;
	height: 0.35rem;
	margin-top: 0.85rem;
	overflow: hidden;
	border-radius: 9999px;
	background: var(--bhasha-100);
}

.bhasha-upload-progress-bar {
	height: 100%;
	border-radius: inherit;
	background: linear-gradient(90deg, var(--bhasha-500), var(--bhasha-700));
	transition: width 300ms ease;
}

.bhasha-uploaded-file {
	display: flex;
	align-items: center;
	gap: 0.85rem;
}

.bhasha-uploaded-file-icon {
	display: grid;
	width: 2.5rem;
	height: 2.5rem;
	flex: 0 0 auto;
	place-items: center;
	border-radius: 0.75rem;
	background: var(--bhasha-50);
	color: var(--bhasha-700);
}

.bhasha-remove-upload {
	display: grid;
	width: 2rem;
	height: 2rem;
	flex: 0 0 auto;
	place-items: center;
	border-radius: 9999px;
	color: #b42318;
	transition:
		background-color 150ms ease,
		color 150ms ease;
}

.bhasha-remove-upload:hover {
	background: #fff1f0;
	color: #8f1710;
}

.bhasha-remove-upload:focus-visible {
	outline: none;
	box-shadow: 0 0 0 3px #fee4e2;
}

[data-dialog='Import Course from ZIP'] .bhasha-dialog-primary:disabled {
	border-color: transparent !important;
	background: #e9e6ed !important;
	color: #918a99 !important;
	box-shadow: none !important;
	transform: none !important;
	cursor: not-allowed;
}

@media (max-width: 639px) {
	.bhasha-zip-dropzone {
		min-height: 10.5rem;
		padding: 1.25rem 0.875rem;
	}
}
</style>
