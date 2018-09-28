package main

import (
	"encoding/binary"
	"errors"
	"io"
	"math"
)

const (
	SizeBool   = 1
	SizeByte   = 1
	SizeShort  = 2
	SizeInt    = 4
	SizeLong   = 8
	SizeSingle = 4
	SizeDouble = 8
)

var (
	ErrWrongSizeRead = errors.New("read wrong number of bytes")
	ErrSkipped       = errors.New("skipped")
)

// readByte reads a byte from r.
func readByte(r io.Reader) (byte, error) {
	b := make([]byte, SizeByte)
	_, err := r.Read(b)
	return b[0], err
}

// readShort reads a short from r.
func readShort(r io.Reader) (uint16, error) {
	b := make([]byte, SizeShort)
	n, err := r.Read(b)
	if err != nil {
		return 0, err
	}

	if n != SizeShort {
		return 0, ErrWrongSizeRead
	}

	return binary.LittleEndian.Uint16(b), nil
}

// readInt reads an int from r.
func readInt(r io.Reader) (uint32, error) {
	b := make([]byte, SizeInt)
	n, err := r.Read(b)
	if err != nil {
		return 0, err
	}

	if n != SizeInt {
		return 0, ErrWrongSizeRead
	}

	return binary.LittleEndian.Uint32(b), nil
}

// readLong reads a long from r.
func readLong(r io.Reader) (uint64, error) {
	b := make([]byte, SizeLong)
	n, err := r.Read(b)
	if err != nil {
		return 0, err
	}

	if n != SizeLong {
		return 0, ErrWrongSizeRead
	}

	return binary.LittleEndian.Uint64(b), nil
}

// readSingle reads a single from r.
func readSingle(r io.Reader) (float32, error) {
	b := make([]byte, SizeSingle)
	n, err := r.Read(b)
	if err != nil {
		return 0, err
	}

	if n != SizeSingle {
		return 0, ErrWrongSizeRead
	}

	return math.Float32frombits(binary.LittleEndian.Uint32(b)), nil
}

// readDouble reads a double from r.
func readDouble(r io.Reader) (float64, error) {
	b := make([]byte, SizeDouble)
	n, err := r.Read(b)
	if err != nil {
		return 0, err
	}

	if n != SizeDouble {
		return 0, ErrWrongSizeRead
	}

	return math.Float64frombits(binary.LittleEndian.Uint64(b)), nil
}

// readBool reads a boolean from r.
func readBool(r io.Reader) (bool, error) {
	n, err := readByte(r)
	return n != 0, err
}

// readULEB reads and decodes a ULEB128 number from f.
// https://en.wikipedia.org/wiki/LEB128#Decode_unsigned_integer
func readULEB(r io.Reader) (uint32, error) {
	n, shift := uint32(0), uint(0)

	for {
		b, err := readByte(r)
		if err != nil {
			return 0, err
		}

		n |= ((uint32(b) & 0x7f) << shift)

		if (b & 0x80) == 0 {
			break
		}

		shift += 7
	}

	return n, nil
}

// readString reads a variable-length string from r.
func readString(r io.Reader) (string, error) {
	if b, err := readByte(r); err != nil {
		return "", err
	} else if b == 0 {
		return "", err
	}

	n, err := readULEB(r)
	if err != nil {
		return "", err
	}

	b := make([]byte, n)
	if _, err := r.Read(b); err != nil {
		return "", err
	}

	return string(b), nil
}

// readString skips over a variable-length string from r.
func skipString(r io.ReadSeeker) error {
	if b, err := readByte(r); err != nil {
		return err
	} else if b == 0 {
		return nil
	}

	n, err := readULEB(r)
	if err != nil {
		return err
	}
	_, err = r.Seek(int64(n), io.SeekCurrent)
	return err
}
